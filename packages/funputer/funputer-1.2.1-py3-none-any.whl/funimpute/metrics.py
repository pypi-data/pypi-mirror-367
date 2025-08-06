"""
Optional metrics collection for observability and monitoring.
Requires: pip install funputer[monitoring]
"""

import time
from typing import Dict, Any
import threading

try:
    from prometheus_client import Gauge, Counter, Histogram, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class MetricsCollector:
    """Optional Prometheus metrics collector for imputation analysis."""
    
    def __init__(self, port: int = 8001):
        self._enabled = PROMETHEUS_AVAILABLE
        if not self._enabled:
            return
            
        self.port = port
        self._server_started = False
        self._lock = threading.Lock()
        
        # Define metrics
        self.columns_processed = Counter(
            'funimpute_columns_processed_total',
            'Total number of columns processed',
            ['data_type', 'mechanism']
        )
        
        self.missing_values_total = Gauge(
            'funimpute_missing_values_total',
            'Total number of missing values across all columns'
        )
        
        self.outliers_total = Gauge(
            'funimpute_outliers_total',
            'Total number of outliers detected across all columns'
        )
        
        self.analysis_duration = Histogram(
            'funimpute_analysis_duration_seconds',
            'Time spent analyzing each column',
            ['column_name', 'data_type'],
            buckets=[0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.total_analysis_duration = Gauge(
            'funimpute_total_analysis_duration_seconds',
            'Total time spent on complete analysis'
        )
        
        self.confidence_score = Gauge(
            'funimpute_confidence_score',
            'Confidence score for imputation suggestions',
            ['method', 'mechanism']
        )
        
        self.data_quality_score = Gauge(
            'funimpute_data_quality_score',
            'Overall data quality assessment score',
            ['dataset']
        )

    def start_server(self) -> None:
        """Start the Prometheus metrics server."""
        if not self._enabled:
            return
            
        with self._lock:
            if not self._server_started:
                start_http_server(self.port)
                self._server_started = True

    def record_column_processed(self, data_type: str, mechanism: str) -> None:
        """Record that a column has been processed."""
        if not self._enabled:
            return
        self.columns_processed.labels(data_type=data_type, mechanism=mechanism).inc()

    def update_missing_values_total(self, count: int) -> None:
        """Update the total count of missing values."""
        if not self._enabled:
            return
        self.missing_values_total.set(count)

    def update_outliers_total(self, count: int) -> None:
        """Update the total count of outliers."""
        if not self._enabled:
            return
        self.outliers_total.set(count)

    def record_analysis_duration(self, column_name: str, data_type: str, duration: float) -> None:
        """Record analysis duration for a column."""
        if not self._enabled:
            return
        self.analysis_duration.labels(column_name=column_name, data_type=data_type).observe(duration)

    def update_total_analysis_duration(self, duration: float) -> None:
        """Update total analysis duration."""
        if not self._enabled:
            return
        self.total_analysis_duration.set(duration)

    def record_confidence_score(self, method: str, mechanism: str, score: float) -> None:
        """Record confidence score for an imputation suggestion."""
        if not self._enabled:
            return
        self.confidence_score.labels(method=method, mechanism=mechanism).set(score)

    def update_data_quality_score(self, dataset: str, score: float) -> None:
        """Update overall data quality score."""
        if not self._enabled:
            return
        self.data_quality_score.labels(dataset=dataset).set(score)

    def calculate_data_quality_score(self, analysis_results: list) -> float:
        """Calculate overall data quality score based on analysis results."""
        if not analysis_results:
            return 0.0
            
        total_columns = len(analysis_results)
        quality_factors = []
        
        for result in analysis_results:
            # Missing data impact (0-1, where 1 is best)
            missing_pct = getattr(result, 'missing_percentage', 0)
            missing_score = max(0, 1 - (missing_pct * 2))  # Heavy penalty for missing data
            
            # Outlier impact (0-1, where 1 is best)
            outlier_pct = getattr(result, 'outlier_percentage', 0)
            outlier_score = max(0, 1 - (outlier_pct * 1.5))  # Moderate penalty for outliers
            
            # Confidence score (already 0-1)
            confidence = getattr(result.imputation_proposal, 'confidence_score', 0.5)
            
            # Weighted average
            column_quality = (missing_score * 0.4 + outlier_score * 0.3 + confidence * 0.3)
            quality_factors.append(column_quality)
        
        # Overall quality score
        overall_score = sum(quality_factors) / total_columns if quality_factors else 0.0
        return min(1.0, max(0.0, overall_score))


# Global metrics instance
_metrics_collector = None


def get_metrics_collector(port: int = 8001) -> MetricsCollector:
    """Get or create the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(port)
    return _metrics_collector


def start_metrics_server(port: int = 8001) -> None:
    """Start the metrics server."""
    collector = get_metrics_collector(port)
    collector.start_server()


class AnalysisTimer:
    """Context manager for timing analysis operations."""
    
    def __init__(self, column_name: str, data_type: str):
        self.column_name = column_name
        self.data_type = data_type
        self.start_time = None
        self.metrics = get_metrics_collector()

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics.record_analysis_duration(self.column_name, self.data_type, duration)


# Alias for backward compatibility
MetricsContext = AnalysisTimer