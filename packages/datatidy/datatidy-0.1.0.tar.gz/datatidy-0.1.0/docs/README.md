# DataTidy Documentation Index

Welcome to DataTidy's complete documentation! This index helps you find everything you need.

## 📖 Core Documentation

### **Quick Start**
- **[Main README](../README.md)** - Project overview, installation, quick examples
- **[Architecture Overview](architecture.md)** - System design and components

### **Complete Reference**
- **[Configuration Reference](configuration.md)** - **📋 COMPREHENSIVE** guide to all features
  - Input configurations (single & multi-source)
  - Join operations and suffix behavior
  - Column transformations & validations
  - Advanced operations (map/reduce/filter)
  - Expression system & functions
  - Complete examples for every feature

## 🎯 Feature Documentation

### **Input Sources**
| Feature | Documentation | Example |
|---------|---------------|---------|
| CSV Files | [Config Ref](configuration.md#csv-input) | [sample_config.yaml](../examples/sample_config.yaml) |
| Excel Files | [Config Ref](configuration.md#excel-input) | [excel_config.yaml](../examples/excel_config.yaml) |
| Databases | [Config Ref](configuration.md#database-input) | [database_config.yaml](../examples/database_config.yaml) |
| Parquet Files | [Config Ref](configuration.md#parquet-input) | [multi_input_config.yaml](../examples/multi_input_config.yaml) |
| Pickle Files | [Config Ref](configuration.md#pickle-input) | [Configuration Reference](configuration.md) |

### **Multi-Input & Joins**
| Feature | Documentation | Example |
|---------|---------------|---------|
| Multi-Input Setup | [Config Ref](configuration.md#multi-input-with-joins-new) | [multi_input_config.yaml](../examples/multi_input_config.yaml) |
| Join Types | [Config Ref](configuration.md#join-types) | [simple_join_config.yaml](../examples/simple_join_config.yaml) |
| Suffix Behavior | [Config Ref](configuration.md#column-suffixes) | [suffix_behavior_demo.yaml](../examples/suffix_behavior_demo.yaml) |
| Join Examples | [Config Ref](configuration.md#multi-input-examples) | [example_multi_input_usage.py](../examples/example_multi_input_usage.py) |

### **Data Transformations**
| Feature | Documentation | Example |
|---------|---------------|---------|
| Basic Expressions | [Config Ref](configuration.md#transformations) | [sample_config.yaml](../examples/sample_config.yaml) |
| Advanced Operations | [Config Ref](configuration.md#advanced-column-operations) | [advanced_column_operations.yaml](../examples/advanced_column_operations.yaml) |
| Lambda Functions | [Config Ref](configuration.md#operation-types) | [lambda_examples.py](../examples/lambda_examples.py) |
| Map Operations | [Config Ref](configuration.md#map-operations) | [advanced_column_operations.yaml](../examples/advanced_column_operations.yaml) |
| Filter Operations | [Config Ref](configuration.md#filter-operations) | [advanced_column_operations.yaml](../examples/advanced_column_operations.yaml) |
| Reduce Operations | [Config Ref](configuration.md#reduce-operations) | [lambda_examples.py](../examples/lambda_examples.py) |
| Window Operations | [Config Ref](configuration.md#window-operations) | [lambda_examples.py](../examples/lambda_examples.py) |
| Chained Operations | [Config Ref](configuration.md#chained-operations) | [advanced_column_operations.yaml](../examples/advanced_column_operations.yaml) |

### **Dependency-Aware Processing**
| Feature | Documentation | Example |
|---------|---------------|---------|
| Basic Dependencies | [Config Ref](configuration.md#dependency-aware-processing) | [basic_dependency_example.yaml](../examples/basic_dependency_example.yaml) |
| Complex Dependencies | [Config Ref](configuration.md#execution-order-resolution) | [complex_dependency_example.yaml](../examples/complex_dependency_example.yaml) |
| Interim Columns | [Config Ref](configuration.md#interim-columns) | [interim_columns_filter_example.yaml](../examples/interim_columns_filter_example.yaml) |
| Execution Planning | [Config Ref](configuration.md#debugging-dependencies) | [execution_plan_debug_example.yaml](../examples/execution_plan_debug_example.yaml) |
| Circular Dependencies | [Config Ref](configuration.md#error-handling) | [circular_dependency_example.yaml](../examples/circular_dependency_example.yaml) |
| Advanced + Dependencies | [Config Ref](configuration.md#advanced-dependency-examples) | [advanced_operations_dependency_example.yaml](../examples/advanced_operations_dependency_example.yaml) |
| Complete Feature Demo | [Config Ref](configuration.md#dependency-aware-processing) | [dependency_aware_config.yaml](../examples/dependency_aware_config.yaml) |

### **Data Validation**
| Feature | Documentation | Example |
|---------|---------------|---------|
| Validation Rules | [Config Ref](configuration.md#validation-rules) | [sample_config.yaml](../examples/sample_config.yaml) |
| Data Types | [Config Ref](configuration.md#data-types) | [Configuration Reference](configuration.md) |
| Error Handling | [Config Ref](configuration.md#global-settings) | [multi_input_config.yaml](../examples/multi_input_config.yaml) |

### **Other Features**
| Feature | Documentation | Example |
|---------|---------------|---------|
| Filters & Sorting | [Config Ref](configuration.md#filters) | [sample_config.yaml](../examples/sample_config.yaml) |
| Global Settings | [Config Ref](configuration.md#global-settings) | [multi_input_config.yaml](../examples/multi_input_config.yaml) |
| CLI Usage | [Main README](../README.md#command-line-usage) | Command examples in README |

## 🚀 Getting Started Paths

### **New Users**
1. **[Main README](../README.md)** - Start here for overview
2. **[sample_config.yaml](../examples/sample_config.yaml)** - Basic example
3. **[Configuration Reference](configuration.md)** - Complete guide

### **Multi-Input Processing**
1. **[Multi-Input Section](configuration.md#multi-input-joins)** - Join documentation
2. **[multi_input_config.yaml](../examples/multi_input_config.yaml)** - Complex example
3. **[example_multi_input_usage.py](../examples/example_multi_input_usage.py)** - Python code

### **Advanced Transformations**
1. **[Advanced Operations](configuration.md#advanced-column-operations)** - Map/reduce/filter
2. **[advanced_column_operations.yaml](../examples/advanced_column_operations.yaml)** - Config examples
3. **[lambda_examples.py](../examples/lambda_examples.py)** - Python examples

### **Database Integration**
1. **[Database Input](configuration.md#database-input)** - Connection setup
2. **[database_config.yaml](../examples/database_config.yaml)** - Example config
3. **[Connection Examples](configuration.md#connection-string-examples)** - All database types

## 🔍 Quick Reference

### **Most Common Configurations**
- **Single CSV processing**: [sample_config.yaml](../examples/sample_config.yaml)
- **Two-table join**: [simple_join_config.yaml](../examples/simple_join_config.yaml)
- **Multi-source ETL**: [multi_input_config.yaml](../examples/multi_input_config.yaml)
- **Advanced operations**: [advanced_column_operations.yaml](../examples/advanced_column_operations.yaml)
- **Dependency resolution**: [basic_dependency_example.yaml](../examples/basic_dependency_example.yaml)
- **Interim columns**: [interim_columns_filter_example.yaml](../examples/interim_columns_filter_example.yaml)

### **Key Concepts**
- **[Join Suffix Behavior](configuration.md#column-suffixes)** - How column names are handled
- **[Expression Security](configuration.md#security-notes)** - What's allowed in transformations
- **[Operation Chaining](configuration.md#chained-operations)** - Combining multiple operations

## 💡 Tips for Finding Information

1. **Search the [Configuration Reference](configuration.md)** - Contains everything
2. **Check [examples/](../examples/)** for working configurations
3. **Browse by feature** using the tables above
4. **Start with simple examples** then explore advanced features

---

**📌 Most Important Files:**
- **[Configuration Reference](configuration.md)** - Complete feature documentation
- **[examples/](../examples/)** - Working examples for every use case
- **[Main README](../README.md)** - Quick start and overview