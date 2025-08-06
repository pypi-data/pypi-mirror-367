# FunPuter - Intelligent Imputation Analysis

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/funputer.svg)](https://pypi.org/project/funputer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Simple, fast, intelligent recommendations for handling missing data with enhanced metadata support.**

FunPuter analyzes your data and suggests the best imputation methods based on:
- **Missing data mechanisms** (MCAR, MAR, MNAR detection)
- **Data types** and statistical properties  
- **Business rules** and column dependencies
- **Enhanced metadata constraints** (nullable, allowed_values, max_length)
- **Adaptive thresholds** based on your dataset characteristics

## 🚀 Quick Start

### Installation
```bash
pip install funputer
```

### Basic Usage

**🤖 Auto-Inference Mode (New!)**
```python
import funimpute

# Let FunPuter intelligently infer metadata from your data
suggestions = funimpute.analyze_imputation_requirements(
    data_path="data.csv"  # No metadata file needed!
)

# Use the suggestions
for suggestion in suggestions:
    print(f"{suggestion.column_name}: {suggestion.proposed_method}")
    print(f"  Rationale: {suggestion.rationale}")
    print(f"  Confidence: {suggestion.confidence_score:.3f}")
```

**📋 Explicit Metadata Mode (Production)**
```python
import funimpute

# For maximum accuracy, provide explicit metadata
suggestions = funimpute.analyze_imputation_requirements(
    metadata_path="metadata.csv",
    data_path="data.csv"
)
```

## 🎯 Enhanced Metadata Support (v1.1.0)

FunPuter now supports comprehensive metadata fields that actively influence imputation recommendations:

### Metadata Schema

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `column_name` | string | Column identifier | `"age"` |
| `data_type` | string | Data type (integer, float, string, categorical, datetime) | `"integer"` |
| `nullable` | boolean | Allow null values | `false` |
| `min_value` | number | Minimum allowed value | `0` |
| `max_value` | number | Maximum allowed value | `120` |
| `max_length` | integer | Maximum string length | `50` |
| `allowed_values` | string | Comma-separated list of allowed values | `"A,B,C"` |
| `unique_flag` | boolean | Require unique values | `true` |
| `dependent_column` | string | Column dependencies | `"age"` |
| `business_rule` | string | Custom validation rules | `"Must be positive"` |
| `description` | string | Human-readable description | `"User age in years"` |

### 🛠️ Creating Metadata

**Method 1: CLI Template Generation**
```bash
# Generate a metadata template from your data
funputer init --data data.csv --output metadata.csv

# Edit the generated file to add constraints
# Then analyze with enhanced metadata
funputer analyze --data data.csv --metadata metadata.csv
```

**Method 2: Manual CSV Creation**
```csv
# metadata.csv
# column_name,data_type,nullable,min_value,max_value,max_length,allowed_values,unique_flag,dependent_column,business_rule,description
user_id,integer,false,,,50,,true,,,"Unique user identifier"
age,integer,false,0,120,,,,,Must be positive,"User age in years"
income,float,true,0,,,,,age,Higher with age,"Annual income in USD"
category,categorical,false,,,10,"A,B,C",,,,"User category classification"
email,string,true,,,255,,true,,,"User email address"
```

### 🎯 Metadata in Action

**Example 1: Nullable Constraints**
```python
# When nullable=False but data has missing values
metadata = ColumnMetadata(
    column_name="age",
    data_type="integer",
    nullable=False,
    min_value=0,
    max_value=120
)

# FunPuter will:
# - Detect nullable constraint violations
# - Recommend immediate data quality fixes
# - Lower confidence score due to constraint violations
```

**Example 2: Allowed Values**
```python
# For categorical data with specific allowed values
metadata = ColumnMetadata(
    column_name="status",
    data_type="categorical",
    allowed_values="active,inactive,pending"
)

# FunPuter will:
# - Validate all values against allowed list
# - Recommend mode imputation using only allowed values
# - Increase confidence when data respects constraints
```

**Example 3: String Length Constraints**
```python
# For string data with length limits
metadata = ColumnMetadata(
    column_name="username",
    data_type="string",
    max_length=20,
    unique_flag=True
)

# FunPuter will:
# - Check string lengths against max_length
# - Recommend imputation respecting length limits
# - Consider uniqueness requirements in recommendations
```

### 📊 Enhanced Analysis Results

```python
# Results now include metadata-aware recommendations
for suggestion in suggestions:
    print(f"Column: {suggestion.column_name}")
    print(f"Method: {suggestion.proposed_method}")
    print(f"Confidence: {suggestion.confidence_score:.3f}")
    print(f"Rationale: {suggestion.rationale}")
    
    # New: Metadata constraint information
    if suggestion.metadata_violations:
        print(f"Violations: {suggestion.metadata_violations}")
    
    # New: Enhanced parameters
    if suggestion.parameters:
        print(f"Parameters: {suggestion.parameters}")
```

## 🚀 Advanced Usage

### Programmatic Metadata Creation
```python
from funimpute.models import ColumnMetadata

metadata = [
    ColumnMetadata(
        column_name="product_code",
        data_type="string",
        max_length=10,
        allowed_values="A1,A2,B1,B2",
        nullable=False,
        description="Product classification code"
    ),
    ColumnMetadata(
        column_name="price",
        data_type="float",
        min_value=0,
        max_value=10000,
        business_rule="Must be non-negative"
    )
]

# Analyze with custom metadata
import pandas as pd
data = pd.read_csv("products.csv")
from funimpute.simple_analyzer import SimpleImputationAnalyzer

analyzer = SimpleImputationAnalyzer()
results = analyzer.analyze_dataframe(data, metadata)
```

### CLI Usage with Enhanced Metadata
```bash
# Generate template with new fields
funputer init --data products.csv --output products_metadata.csv

# Edit metadata.csv to add constraints, then:
funputer analyze --data products.csv --metadata products_metadata.csv --output results.json

# View results
funputer report --input results.json --format table
```

## 📋 Requirements

- **Python**: 3.9 or higher
- **Dependencies**: pandas, numpy, scipy, scikit-learn

## 🔧 Installation from Source

```bash
git clone https://github.com/RajeshRamachander/funputer.git
cd funputer
pip install -e .
```

## 📚 Documentation

- **Full API Reference**: [GitHub Wiki](https://github.com/RajeshRamachander/funputer/wiki)
- **Examples**: [Examples Directory](https://github.com/RajeshRamachander/funputer/tree/main/examples)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Focus**: Get intelligent imputation recommendations with enhanced metadata support, not complex infrastructure.