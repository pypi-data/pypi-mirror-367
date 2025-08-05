# DataTidy Examples

This directory contains comprehensive examples demonstrating all DataTidy features using separate YAML configuration files.

## 📁 Configuration Files

### **Basic Examples**
- **[sample_config.yaml](sample_config.yaml)** - Basic single-input CSV processing with transformations and validations
- **[excel_config.yaml](excel_config.yaml)** - Excel file processing with sheet selection
- **[database_config.yaml](database_config.yaml)** - Database connection and SQL query processing

### **Multi-Input & Joins**
- **[simple_join_config.yaml](simple_join_config.yaml)** - Basic two-table join (CSV + Excel)
- **[multi_input_config.yaml](multi_input_config.yaml)** - Complex multi-source joins (CSV + Parquet + Database)
- **[suffix_behavior_demo.yaml](suffix_behavior_demo.yaml)** - Detailed join suffix behavior examples

### **Advanced Column Operations**
- **[advanced_column_operations.yaml](advanced_column_operations.yaml)** - Map/reduce/filter operations with lambda functions

### **Dependency-Aware Processing** 🆕
- **[basic_dependency_example.yaml](basic_dependency_example.yaml)** - Basic dependency resolution with wrong column order
- **[complex_dependency_example.yaml](complex_dependency_example.yaml)** - Multi-level dependencies with interim columns
- **[interim_columns_filter_example.yaml](interim_columns_filter_example.yaml)** - Using interim columns in filters
- **[execution_plan_debug_example.yaml](execution_plan_debug_example.yaml)** - Debugging execution plans
- **[circular_dependency_example.yaml](circular_dependency_example.yaml)** - Circular dependency detection (error demo)
- **[advanced_operations_dependency_example.yaml](advanced_operations_dependency_example.yaml)** - Advanced operations with dependencies
- **[dependency_aware_config.yaml](dependency_aware_config.yaml)** - Comprehensive dependency features demo

### **Time Series & Lag Operations** 🆕
- **[lag_operations_example.yaml](lag_operations_example.yaml)** - Basic lag operations with shift() function
- **[advanced_lag_example.yaml](advanced_lag_example.yaml)** - Advanced trading signals using multiple lag periods
- **[lag_chain_combinations.yaml](lag_chain_combinations.yaml)** - Combining lag operations with chained operations

## 🐍 Python Examples

### **Working Code Examples**
- **[example_usage.py](example_usage.py)** - Basic DataTidy usage patterns
- **[example_multi_input_usage.py](example_multi_input_usage.py)** - Multi-input processing examples
- **[dependency_examples.py](dependency_examples.py)** - Dependency-aware processing using YAML configs
- **[lambda_examples.py](lambda_examples.py)** - Advanced lambda operations examples
- **[lag_operations_examples.py](lag_operations_examples.py)** - Time series analysis with lag operations
- **[lag_chain_examples.py](lag_chain_examples.py)** - Combining lag operations with chained operations

### **Sample Data Files**
- **[sample_data.csv](sample_data.csv)** - Basic sample dataset

## Quick Start

1. **Test with sample data:**
   ```bash
   datatidy process sample_config.yaml -i sample_data.csv -o output.csv
   ```

2. **Run Python examples:**
   ```bash
   python example_usage.py
   ```

3. **Validate configurations:**
   ```bash
   datatidy validate sample_config.yaml
   datatidy validate database_config.yaml
   datatidy validate excel_config.yaml
   ```

## Configuration Features Demonstrated

### Basic Features
- Column mapping and renaming
- Data type conversions
- Simple transformations
- Basic validation rules

### Advanced Features
- Complex transformation expressions
- Conditional logic
- String manipulation
- Mathematical calculations
- Date/time formatting
- Regular expression validation
- Multi-level sorting
- Row filtering

### Database Integration
- SQL query execution
- Connection string management
- Chunked processing for large datasets
- Join operations

### Excel Processing
- Multi-sheet handling
- Custom header rows
- Column range selection
- Advanced formatting

## Common Use Cases

### Data Cleaning
```yaml
columns:
  clean_name:
    source: "name"
    transformation: "str.strip().title()"
    validation:
      min_length: 2
      pattern: "^[A-Za-z\\s]+$"
```

### Data Categorization
```yaml
columns:
  age_group:
    transformation: |
      'senior' if age > 65 else (
        'adult' if age >= 18 else 'minor'
      )
    validation:
      allowed_values: ["senior", "adult", "minor"]
```

### Format Standardization
```yaml
columns:
  formatted_date:
    source: "date_string"
    type: datetime
    format: "%Y-%m-%d"
  
  normalized_phone:
    transformation: "phone.replace('-', '').replace(' ', '')"
    validation:
      pattern: "^\\d{10}$"
```

### Data Enrichment
```yaml
columns:
  full_address:
    transformation: "street + ', ' + city + ', ' + state + ' ' + zip_code"
  
  bmi:
    transformation: "round(weight_kg / ((height_cm / 100) ** 2), 1)"
    validation:
      min_value: 10.0
      max_value: 50.0
```

## Error Handling Patterns

### Strict Validation
```yaml
global_settings:
  ignore_errors: false
  max_errors: 0
```

### Lenient Processing
```yaml
global_settings:
  ignore_errors: true
  max_errors: 100
```

### Default Values for Missing Data
```yaml
columns:
  status:
    source: "status_code"
    default: "Unknown"
    transformation: "'Active' if status_code == 1 else 'Inactive'"
```

## Performance Tips

1. **Use vectorized operations when possible**
2. **Filter early to reduce processing overhead**
3. **Use appropriate data types**
4. **Consider chunked processing for large datasets**

## Security Considerations

DataTidy uses a safe expression parser that:
- Blocks dangerous operations (file access, imports, exec)
- Whitelist of allowed functions and operators
- AST-based validation for security

Safe expressions only!
```yaml
# ✅ Safe
transformation: "str.upper()"
transformation: "'high' if score > 80 else 'low'"
transformation: "round(price * 1.1, 2)"

# ❌ Unsafe (will be blocked)
transformation: "__import__('os').system('rm -rf /')"
transformation: "open('/etc/passwd').read()"
```