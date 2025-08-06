"""
Automatic metadata inference from pandas DataFrames.

This module provides intelligent inference of column metadata when no explicit 
metadata file is provided, making funimputer more accessible while maintaining accuracy.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import re

from .models import ColumnMetadata

logger = logging.getLogger(__name__)


class MetadataInferenceEngine:
    """Intelligent metadata inference engine for pandas DataFrames."""
    
    def __init__(self, 
                 categorical_threshold_ratio: float = 0.1,
                 categorical_threshold_absolute: int = 50,
                 datetime_sample_size: int = 100,
                 min_rows_for_stats: int = 10):
        """
        Initialize the inference engine.
        
        Args:
            categorical_threshold_ratio: Ratio of unique values to total for categorical detection
            categorical_threshold_absolute: Absolute max unique values for categorical
            datetime_sample_size: Number of samples to check for datetime patterns
            min_rows_for_stats: Minimum rows needed for statistical analysis
        """
        self.categorical_threshold_ratio = categorical_threshold_ratio
        self.categorical_threshold_absolute = categorical_threshold_absolute
        self.datetime_sample_size = datetime_sample_size
        self.min_rows_for_stats = min_rows_for_stats
        
        # Common datetime patterns to detect
        self.datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{2}/\d{2}/\d{2}',  # MM/DD/YY
        ]
        
        # Common boolean representations
        self.boolean_values = {
            'true', 'false', 'yes', 'no', '1', '0', 
            'y', 'n', 't', 'f', 'on', 'off'
        }
    
    def infer_dataframe_metadata(self, df: pd.DataFrame, 
                                warn_user: bool = True) -> List[ColumnMetadata]:
        """
        Infer metadata for all columns in a DataFrame.
        
        Args:
            df: DataFrame to analyze
            warn_user: Whether to warn about inference limitations
            
        Returns:
            List of ColumnMetadata objects
        """
        if warn_user:
            logger.warning(
                "🤖 AUTO-INFERRING METADATA: No metadata file provided. "
                "Using intelligent inference with reduced accuracy. "
                "For best results, provide explicit metadata file."
            )
        
        logger.info(f"Inferring metadata for {len(df.columns)} columns in DataFrame with {len(df)} rows")
        
        metadata_list = []
        
        for column_name in df.columns:
            try:
                metadata = self._infer_column_metadata(df, column_name)
                metadata_list.append(metadata)
                logger.debug(f"Inferred {column_name}: {metadata.data_type}")
            except Exception as e:
                logger.warning(f"Failed to infer metadata for column '{column_name}': {e}")
                # Fallback to string type
                fallback_metadata = ColumnMetadata(
                    column_name=str(column_name),
                    data_type='string',
                    nullable=True,
                    description=f"Fallback inference (error: {str(e)[:50]})"
                )
                metadata_list.append(fallback_metadata)
        
        logger.info(f"Successfully inferred metadata for {len(metadata_list)} columns")
        return metadata_list
    
    def _infer_column_metadata(self, df: pd.DataFrame, column_name: str) -> ColumnMetadata:
        """Infer metadata for a single column."""
        series = df[column_name]
        
        # Basic info
        total_count = len(series)
        null_count = series.isnull().sum()
        non_null_series = series.dropna()
        
        # Determine data type
        data_type = self._infer_data_type(series, non_null_series)
        
        # Determine constraints
        min_value, max_value, max_length = self._infer_constraints(non_null_series, data_type)
        
        # Determine uniqueness
        unique_flag = self._infer_uniqueness(non_null_series, total_count)
        
        # Generate description
        description = self._generate_description(series, data_type, unique_flag)
        
        return ColumnMetadata(
            column_name=str(column_name),
            data_type=data_type,
            min_value=min_value,
            max_value=max_value,
            max_length=max_length,
            unique_flag=unique_flag,
            nullable=(null_count > 0),
            description=description
        )
    
    def _infer_data_type(self, series: pd.Series, non_null_series: pd.Series) -> str:
        """Infer the data type of a series."""
        if len(non_null_series) == 0:
            return 'string'  # Default for all-null columns
        
        # Check pandas dtype first
        dtype_str = str(series.dtype).lower()
        
        # Handle numeric types
        if pd.api.types.is_integer_dtype(series):
            return 'integer'
        elif pd.api.types.is_float_dtype(series):
            return 'integer' if self._could_be_integer(non_null_series) else 'float'
        elif pd.api.types.is_bool_dtype(series):
            return 'boolean'
        elif pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        
        # Handle object/string columns - need deeper analysis
        if dtype_str in ['object', 'string']:
            return self._infer_object_type(non_null_series)
        
        # Handle categorical
        if pd.api.types.is_categorical_dtype(series):
            return 'categorical'
        
        # Default fallback
        return 'string'
    
    def _could_be_integer(self, series: pd.Series) -> bool:
        """Check if float series could actually be integer."""
        if not pd.api.types.is_float_dtype(series):
            return False
        
        # Check if all non-null values are whole numbers
        non_null = series.dropna()
        if len(non_null) == 0:
            return False
            
        return np.all(non_null == non_null.astype(int))
    
    def _infer_object_type(self, series: pd.Series) -> str:
        """Infer type for object/string columns."""
        sample_size = min(len(series), self.datetime_sample_size)
        sample = series.head(sample_size)
        
        # Check for datetime patterns
        if self._is_datetime_column(sample):
            return 'datetime'
        
        # Check for boolean patterns
        if self._is_boolean_column(sample):
            return 'boolean'
        
        # Check for numeric strings
        if self._is_numeric_string_column(sample):
            return 'float' if self._has_decimal_numbers(sample) else 'integer'
        
        # Check for categorical
        if self._is_categorical_column(series):
            return 'categorical'
        
        return 'string'
    
    def _is_datetime_column(self, sample: pd.Series) -> bool:
        """Check if string column contains datetime values."""
        if len(sample) == 0:
            return False
        
        # Try pandas datetime parsing
        try:
            parsed = pd.to_datetime(sample, errors='coerce')
            valid_ratio = parsed.notna().sum() / len(sample)
            if valid_ratio > 0.8:  # 80% valid dates
                return True
        except:
            pass
        
        # Check regex patterns
        string_sample = sample.astype(str)
        for pattern in self.datetime_patterns:
            matches = string_sample.str.match(pattern, na=False).sum()
            if matches / len(sample) > 0.8:
                return True
        
        return False
    
    def _is_boolean_column(self, sample: pd.Series) -> bool:
        """Check if column contains boolean values."""
        if len(sample) == 0:
            return False
        
        unique_values = set(str(v).lower().strip() for v in sample.unique())
        return unique_values.issubset(self.boolean_values)
    
    def _is_numeric_string_column(self, sample: pd.Series) -> bool:
        """Check if string column contains numeric values."""
        if len(sample) == 0:
            return False
        
        try:
            numeric_converted = pd.to_numeric(sample, errors='coerce')
            valid_ratio = numeric_converted.notna().sum() / len(sample)
            return valid_ratio > 0.8  # 80% valid numbers
        except:
            return False
    
    def _has_decimal_numbers(self, sample: pd.Series) -> bool:
        """Check if numeric strings contain decimal numbers."""
        try:
            numeric_converted = pd.to_numeric(sample, errors='coerce')
            non_null = numeric_converted.dropna()
            if len(non_null) == 0:
                return False
            return not np.all(non_null == non_null.astype(int))
        except:
            return False
    
    def _is_categorical_column(self, series: pd.Series) -> bool:
        """Determine if a string column should be treated as categorical."""
        if len(series) < 2:
            return False
        
        unique_count = series.nunique()
        total_count = len(series)
        
        # Use both ratio and absolute thresholds
        ratio_check = (unique_count / total_count) <= self.categorical_threshold_ratio
        absolute_check = unique_count <= self.categorical_threshold_absolute
        
        return ratio_check or absolute_check
    
    def _infer_constraints(self, series: pd.Series, data_type: str) -> Tuple[Optional[float], Optional[float], Optional[int]]:
        """Infer min/max values and max length constraints."""
        min_value = None
        max_value = None
        max_length = None
        
        if len(series) == 0:
            return min_value, max_value, max_length
        
        try:
            if data_type in ['integer', 'float']:
                # Set constraints if we have any data (be more permissive for small datasets)
                if len(series) >= 2:  # Need at least 2 values
                    min_value = float(series.min())
                    max_value = float(series.max())
            
            elif data_type in ['string', 'categorical']:
                # Get maximum string length
                string_lengths = series.astype(str).str.len()
                max_length = int(string_lengths.max()) if len(string_lengths) > 0 else None
        
        except Exception as e:
            logger.debug(f"Failed to infer constraints: {e}")
        
        return min_value, max_value, max_length
    
    def _infer_uniqueness(self, series: pd.Series, total_count: int) -> bool:
        """Infer if column values should be unique."""
        if len(series) == 0 or total_count == 0:
            return False
        
        unique_count = series.nunique()
        
        # Check for ID-like column names first
        column_name = str(series.name).lower() if series.name else ""
        id_indicators = ['id', 'key', 'pk', 'uuid', 'guid', '_id', 'identifier']
        has_id_name = any(indicator in column_name for indicator in id_indicators)
        
        # Be conservative about uniqueness - only flag as unique if:
        # 1. Column name suggests it's an ID, OR
        # 2. All values are unique AND we have sufficient data AND values look like IDs
        if has_id_name and unique_count == len(series):
            return True
        
        # For non-ID named columns, require more evidence
        if unique_count == len(series) and len(series) >= 20:  # Need more data points
            # Check if values look like identifiers (sequential integers, etc.)
            if series.dtype in ['int64', 'int32'] and len(series) > 1:
                # Check if it's a sequential ID (common pattern)
                sorted_vals = sorted(series.dropna())
                if len(sorted_vals) >= 2:
                    diffs = [sorted_vals[i+1] - sorted_vals[i] for i in range(len(sorted_vals)-1)]
                    # If mostly sequential (diff of 1), it's likely an ID
                    if sum(1 for d in diffs if d == 1) / len(diffs) > 0.8:
                        return True
        
        return False
    
    def _generate_description(self, series: pd.Series, data_type: str, unique_flag: bool) -> str:
        """Generate a helpful description for the inferred column."""
        descriptions = []
        
        # Add type info
        descriptions.append(f"Auto-inferred {data_type} column")
        
        # Add uniqueness info
        if unique_flag:
            descriptions.append("appears to be unique identifier")
        
        # Add data characteristics
        null_pct = (series.isnull().sum() / len(series)) * 100 if len(series) > 0 else 0
        if null_pct > 10:
            descriptions.append(f"{null_pct:.1f}% missing values")
        
        if data_type == 'categorical' and len(series) > 0:
            unique_count = series.nunique()
            descriptions.append(f"{unique_count} unique categories")
        
        return "; ".join(descriptions)


# Convenience function for easy import
def infer_metadata_from_dataframe(df: pd.DataFrame, warn_user: bool = True, **kwargs) -> List[ColumnMetadata]:
    """
    Convenience function to infer metadata from a DataFrame.
    
    Args:
        df: DataFrame to analyze
        warn_user: Whether to warn user about inference limitations
        **kwargs: Additional parameters for MetadataInferenceEngine
        
    Returns:
        List of ColumnMetadata objects
    """
    engine = MetadataInferenceEngine(**kwargs)
    return engine.infer_dataframe_metadata(df, warn_user=warn_user)