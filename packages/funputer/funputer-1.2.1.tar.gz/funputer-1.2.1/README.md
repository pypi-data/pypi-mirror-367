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

## 🎯 Enhanced Features (v1.2.1)

**What's New in v1.2.1:**
- 🚨 **PREFLIGHT System**: Lean validation that runs before ANY analysis - prevents crashes!
- 🔍 **Smart Auto-Inference**: Intelligent metadata detection with confidence scoring
- ⚡ **Constraint Validation**: Real-time nullable, allowed_values, and max_length checking
- 🎯 **Enhanced Proposals**: Metadata-aware imputation method selection
- 🛡️ **Exception Detection**: Comprehensive constraint violation handling
- 📈 **Improved Confidence**: Dynamic scoring based on metadata compliance
- 🧹 **Warning Suppression**: Clean output with optimized pandas datetime parsing

## 🚨 PREFLIGHT System (NEW!)

**Fast validation to prevent crashes and guide your workflow**

### What PREFLIGHT Does
- **Runs automatically** before `init` and `analyze` commands
- **8 core checks** (A1-A8): file access, format detection, encoding, structure, memory estimation
- **Advisory recommendations**: "generate metadata first" vs "analyze now"
- **Zero crashes**: Catches problems before they break your workflow
- **Backward compatible**: All existing commands work exactly as before

### Independent Usage
```bash
# Basic preflight check
funimputer preflight -d your_data.csv

# With custom options
funimputer preflight -d data.csv --sample-rows 5000 --encoding utf-8

# JSON report output
funimputer preflight -d data.csv --json-out report.json
```

### Exit Codes
- **0**: ✅ Ready for analysis
- **2**: ⚠️ OK with warnings (can proceed)
- **10**: ❌ Hard error (cannot proceed)

### Example Output
```bash
🔍 PREFLIGHT REPORT
==================================================
Status: ✅ OK
File: data.csv
Size: 2.5 MB (csv)  
Columns: 12
Recommendation: Analyze Infer Only
```

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
funimputer init -d data.csv -o metadata.csv

# Edit the generated file to add constraints
# Then analyze with enhanced metadata
funimputer analyze -d data.csv -m metadata.csv
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

## 🔍 Confidence-Score Heuristics

FunPuter assigns a **`confidence_score`** (range **0 – 1**) to every imputation recommendation.  The value is a transparent, rule-based estimate of how reliable the proposed method is, **not** a formal statistical uncertainty.  Two calculators are used:

### Base heuristic
When only column-level data is available (no full DataFrame), the score is computed as follows:

| Signal | Condition | Δ Score |
|--------|-----------|---------|
| **Starting value** | | **0.50** |
| Missing % | `< 5 %` +0.20 • `5 – 20 %` +0.10 • `> 50 %` −0.20 |
| Mechanism | MCAR (weak evidence) +0.10 • MAR (related cols) +0.05 • MNAR/UNKNOWN −0.10 |
| Outliers | `< 5 %` +0.05 • `> 20 %` −0.10 |
| Metadata constraints | `allowed_values` (categorical/string) +0.10 • `max_length` (string) +0.05 |
| Nullable constraint | `nullable=False` **with** missing −0.15 • **without** missing +0.05 |
| Data-quality checks | Strings within `max_length` +0.05 • Categorical values inside `allowed_values` + *(valid_ratio × 0.10)* |

The final score is clipped to the **[0.10, 1.00]** interval.

### Adaptive variant
When the analyzer receives the full DataFrame **and** complete metadata, it builds dataset-specific thresholds using `AdaptiveThresholds` and applies `calculate_adaptive_confidence_score`:

* Adaptive missing/outlier thresholds (based on row-count, variability, etc.)
* An additional adjustment factor (−0.30 … +0.30) reflecting dataset characteristics

This yields a context-aware score that remains interpretable yet sensitive to each dataset.

### Future work
For maximum transparency and speed we use heuristics today.  Future releases may include probabilistic or conformal approaches (e.g., multiple-imputation variance or ensemble uncertainty) to provide statistically grounded confidence estimates.

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

### CLI Usage with Enhanced Metadata & PREFLIGHT
```bash
# PREFLIGHT runs automatically before init/analyze
funimputer init -d products.csv -o products_metadata.csv
# 🔍 Preflight Check: ✅ OK - File validated, ready for processing

# Edit metadata.csv to add constraints, then:
funimputer analyze -d products.csv -m products_metadata.csv -o results.csv
# 🔍 Preflight Check: ✅ OK - Recommendation: Analyze Now

# Run standalone preflight validation
funimputer preflight -d products.csv --json-out validation_report.json

# Disable preflight if needed (not recommended)
export FUNPUTER_PREFLIGHT=off
funimputer analyze -d products.csv

# Results are automatically saved in CSV format for easy viewing
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