# DataTidy Configuration Reference

This document provides a complete reference for DataTidy YAML configuration files.

## Configuration Structure

A DataTidy configuration file has three main sections:

```yaml
input:          # Data source configuration
output:         # Column definitions and output settings
global_settings: # Processing options (optional)
```

## Input Configuration

DataTidy supports both single-input and multi-input configurations with joins.

### Single Input (Traditional)

```yaml
input:
  type: <source_type>        # Required: csv, excel, database, parquet, pickle
  source: <source_path>      # Required: file path or SQL query
  connection_string: <conn>  # Optional: for database connections
  options: <options_dict>    # Optional: reader-specific options
```

### Multi-Input with Joins (New)

```yaml
inputs:                      # Multiple named input sources
  <dataset_name1>:
    type: <source_type>
    source: <source_path>
    connection_string: <conn>  # Optional
    options: <options_dict>    # Optional
    
  <dataset_name2>:
    type: <source_type>
    source: <source_path>

joins:                       # Optional: join operations
  - left: <dataset_name1>
    right: <dataset_name2>
    on: <join_keys>
    how: <join_type>         # inner, left, right, outer, cross
    suffix: [<left_suffix>, <right_suffix>]  # Optional
```

### CSV Input

```yaml
input:
  type: csv
  source: "path/to/file.csv"
  options:
    encoding: utf-8          # File encoding (default: utf-8)
    delimiter: ","           # Column separator (default: ,)
    header: 0                # Header row index (default: 0)
    skiprows: 0              # Rows to skip at start
    nrows: 1000              # Maximum rows to read
    na_values: ["", "NULL"]  # Values to treat as null
```

### Excel Input

```yaml
input:
  type: excel
  source:
    path: "path/to/file.xlsx"
    sheet_name: "Sheet1"     # Sheet name or index (default: 0)
    options:
      header: 0              # Header row index
      skiprows: 2            # Rows to skip at start
      usecols: "A:E"         # Columns to read
```

### Database Input

```yaml
input:
  type: database
  source:
    query: "SELECT * FROM users WHERE active = true"
    connection_string: "postgresql://user:pass@localhost/db"
  # OR use global connection string
  source: "SELECT * FROM users"
  connection_string: "postgresql://user:pass@localhost/db"
```

### Parquet Input

```yaml
input:
  type: parquet
  source: "path/to/file.parquet"
  options:
    columns: ["col1", "col2"]    # Columns to read
    filters: [("col1", ">", 100)]  # Row filters
```

### Pickle Input

```yaml
input:
  type: pickle
  source: "path/to/file.pkl"
```

#### Supported Input Types
- `csv` - Comma-separated values
- `excel`, `xlsx`, `xls` - Excel files
- `parquet` - Apache Parquet format
- `pickle` - Python pickle files
- `database`, `db`, `sql` - Generic database
- `postgres`, `postgresql` - PostgreSQL
- `mysql` - MySQL/MariaDB
- `snowflake` - Snowflake

#### Connection String Examples

**PostgreSQL:**
```
postgresql://username:password@hostname:port/database_name
```

**MySQL:**
```
mysql://username:password@hostname:port/database_name
```

**Snowflake:**
```
snowflake://username:password@account/database/schema?warehouse=warehouse_name
```

## Multi-Input Joins

When using multiple input sources, you can join them using the `joins` section.

### Join Configuration

```yaml
joins:
  - left: <left_dataset>      # Left dataset name  
    right: <right_dataset>    # Right dataset name
    on: <join_specification>  # How to join
    how: <join_type>          # Join method
    suffix: [<left>, <right>] # Column name suffixes
```

### Join Types

| Type | Description | Example Use Case |
|------|-------------|------------------|
| `inner` | Only matching records | Users with orders |
| `left` | All left records, matching right | All users, with order data if available |
| `right` | All right records, matching left | All orders, with user data if available |
| `outer` | All records from both sides | Complete dataset union |
| `cross` | Cartesian product | Generate all combinations |

### Join Key Specifications

#### Simple Column Name
```yaml
on: "user_id"              # Same column name in both datasets
```

#### List of Columns
```yaml
on: ["user_id", "region"]  # Multiple columns, same names
```

#### Different Column Names
```yaml
on:
  left: "user_id"
  right: "customer_id"
```

#### Column Mapping
```yaml
on:
  user_id: customer_id     # left_col: right_col
  region_id: region_code
```

### Column Suffixes

When datasets have overlapping column names, suffixes are automatically added to resolve conflicts.

#### Suffix Behavior Rules

1. **Only applied to conflicting columns** - Columns with the same name in both datasets
2. **Join keys are never suffixed** - The join column keeps its original name
3. **Unique columns keep original names** - No suffix added
4. **Must specify exactly 2 strings** - `[left_suffix, right_suffix]`
5. **Default if not specified** - `["_left", "_right"]`

#### Suffix Examples

**Input datasets:**
```
Users:     id, name, email        
Orders:    id, user_id, name, total
```

**Join configuration:**
```yaml
suffix: ["_user", "_order"]
```

**Result columns:**
- `user_id` - Join key (no suffix)
- `email` - Unique to users (no suffix)  
- `total` - Unique to orders (no suffix)
- `id_user` - Conflicting column from users
- `id_order` - Conflicting column from orders
- `name_user` - Conflicting column from users
- `name_order` - Conflicting column from orders

#### Special Suffix Cases

```yaml
# Keep left table names unchanged
suffix: ["", "_right"]
# Result: name (from left), name_right (from right)

# Use descriptive names
suffix: ["_customer", "_product"] 
# Result: name_customer, name_product

# Default behavior (if suffix not specified)
suffix: ["_left", "_right"]
# Result: name_left, name_right
```

### Multi-Input Examples

#### Example 1: E-commerce Data Join

```yaml
inputs:
  users:
    type: csv
    source: "users.csv"
  
  orders:
    type: parquet  
    source: "orders.parquet"
    
  products:
    type: database
    source: "SELECT * FROM products"
    connection_string: "postgresql://..."

joins:
  # Join users with their orders
  - left: users
    right: orders
    on: user_id
    how: inner
    suffix: ["_user", "_order"]
    
  # Add product information
  - left: result           # Reference previous join result
    right: products
    on:
      left: product_id
      right: id
    how: left

output:
  columns:
    customer_name:
      source: "name_user"  # Column with suffix from join
      transformation: "str.title()"
      
    product_name:
      source: "name"       # Product name (no suffix needed)
      
    order_summary:
      transformation: "f'{customer_name} bought {product_name}'"
```

#### Example 2: Cross Join for Combinations

```yaml
inputs:
  colors:
    type: csv
    source: "colors.csv"    # Contains: Red, Blue, Green
    
  sizes:
    type: csv  
    source: "sizes.csv"     # Contains: Small, Large

joins:
  - left: colors
    right: sizes
    how: cross

output:
  columns:
    product_variant:
      transformation: "f'{size} {color} Shirt'"
```

#### Example 3: Multiple Sequential Joins

```yaml
inputs:
  employees:
    type: excel
    source: "employees.xlsx"
    
  departments:
    type: csv
    source: "departments.csv"
    
  locations:
    type: database
    source: "SELECT * FROM office_locations"

joins:
  # First: employees with departments
  - left: employees  
    right: departments
    on: dept_id
    how: left
    suffix: ["", "_dept"]
    
  # Second: add location information  
  - left: result
    right: locations
    on:
      left: location_id_dept
      right: id
    how: left
    suffix: ["", "_loc"]

output:
  columns:
    employee_info:
      transformation: "f'{name} works in {name_dept} at {city_loc}'"
```

## Output Configuration

The `output` section defines how to transform and validate your data.

### Basic Structure

```yaml
output:
  columns:     # Column definitions (required)
    <column_name>:
      source: <source_column>
      type: <data_type>
      transformation: <expression>
      validation: <rules>
      default: <default_value>
  filters:     # Row filtering (optional)
  sort:        # Result sorting (optional)
```

### Column Definitions

Each output column is defined with these properties:

#### Required Properties
- Column name must be a valid identifier (letters, numbers, underscores)

#### Optional Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `source` | string | Source column name or expression | Column name |
| `type` | string | Data type: `string`, `int`, `float`, `bool`, `datetime` | `string` |
| `format` | string | Format string for datetime parsing | Auto-detect |
| `transformation` | string | Python expression for data transformation | None |
| `operations` | array | Advanced column operations (map/reduce/filter) | None |
| `interim` | boolean | Mark as interim column (excluded from final output) | `false` |
| `validation` | object | Validation rules | `{required: true, nullable: false}` |
| `default` | any | Default value for null/missing data | None |

#### Example Column Definitions

```yaml
output:
  columns:
    # Simple column mapping
    user_id:
      source: "id"
      type: int
    
    # String transformation
    full_name:
      source: "name"
      type: string
      transformation: "str.strip().title()"
    
    # Conditional expression
    age_group:
      transformation: "'adult' if age >= 18 else 'minor'"
      type: string
    
    # Date formatting
    signup_date:
      source: "registration_date"
      type: datetime
      format: "%Y-%m-%d"
    
    # With default value
    department:
      source: "dept"
      type: string
      default: "General"
```

### Data Types

| Type | Description | Example Values |
|------|-------------|----------------|
| `string` | Text data | `"Hello World"` |
| `int` | Integer numbers | `42`, `-10` |
| `float` | Decimal numbers | `3.14`, `-2.5` |
| `bool` | True/False values | `true`, `false` |
| `datetime` | Date/time values | `2023-12-25`, `2023-12-25 10:30:00` |

### Transformations

Transformations are Python expressions that can reference column values and use safe operations.

#### Available Operations
- **Arithmetic:** `+`, `-`, `*`, `/`, `//`, `%`, `**`
- **Comparison:** `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Logical:** `and`, `or`, `not`
- **Membership:** `in`, `not in`

#### Available Functions
- **Type conversion:** `str()`, `int()`, `float()`, `bool()`
- **Math:** `abs()`, `max()`, `min()`, `round()`
- **String methods:** `upper()`, `lower()`, `strip()`, `replace()`, etc.

#### Transformation Examples

```yaml
# String operations
clean_name: "name.strip().title()"
email_domain: "email.split('@')[1] if '@' in email else ''"

# Mathematical calculations
bmi: "round(weight / (height / 100) ** 2, 1)"
tax_amount: "price * 0.08"

# Conditional logic
status: "'active' if last_login_days < 30 else 'inactive'"
grade: "'A' if score >= 90 else ('B' if score >= 80 else 'C')"

# Complex expressions
risk_score: |
  (
    age * 0.1 + 
    (1 if smoker else 0) * 20 + 
    max(0, cholesterol - 200) * 0.05
  )
```

### Validation Rules

Validation rules ensure data quality and consistency.

#### Available Rules

| Rule | Type | Description | Example |
|------|------|-------------|---------|
| `required` | boolean | Field must not be null | `required: true` |
| `nullable` | boolean | Field can be null | `nullable: false` |
| `min_value` | number | Minimum numeric value | `min_value: 0` |
| `max_value` | number | Maximum numeric value | `max_value: 100` |
| `min_length` | integer | Minimum string length | `min_length: 2` |
| `max_length` | integer | Maximum string length | `max_length: 50` |
| `pattern` | string | Regular expression pattern | `pattern: "^[A-Za-z]+$"` |
| `allowed_values` | array | Whitelist of allowed values | `allowed_values: ["A", "B", "C"]` |

#### Validation Examples

```yaml
output:
  columns:
    email:
      validation:
        required: true
        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    
    age:
      validation:
        required: true
        min_value: 0
        max_value: 120
    
    category:
      validation:
        allowed_values: ["high", "medium", "low"]
    
    name:
      validation:
        required: true
        min_length: 2
        max_length: 100
        pattern: "^[A-Za-z\\s]+$"
```

## Advanced Column Operations

DataTidy supports sophisticated single-column operations using `operations` instead of `transformation`. These operations support lambda functions and can be chained together.

### Operation Types

#### Map Operations
Apply a function to each element in a column.

```yaml
cleaned_text:
  source: "raw_text"
  operations:
    - type: map
      function: "lambda x: str(x).strip().lower().replace('_', ' ')"
  type: string
```

#### Filter Operations  
Keep only elements that match a condition, replace others with a fill value.

```yaml
high_values:
  source: "value"
  operations:
    - type: filter
      condition: "lambda x: x > 100"
      fill_value: 0
  type: float
```

#### Reduce Operations
Aggregate all column values into a single result (broadcast to all rows).

```yaml
running_total:
  source: "amount"
  operations:
    - type: reduce
      function: "lambda acc, x: acc + x"
      initial_value: 0
  type: float
```

#### Group Operations
Apply group-based aggregations.

```yaml
category_average:
  source: "value"
  operations:
    - type: group
      group_by: "category"
      function: "mean"
  type: float
```

#### Window Operations
Apply rolling window calculations.

```yaml
moving_average:
  source: "value"  
  operations:
    - type: window
      window_size: 3
      function: "mean"
  type: float
```

### Chained Operations

Operations can be chained to create complex transformations:

```yaml
processed_data:
  source: "raw_data"
  operations:
    - type: map
      function: "lambda x: str(x).strip().lower()"    # Clean
    - type: filter
      condition: "lambda x: len(x) > 3"               # Filter short strings
      fill_value: "invalid"
    - type: map  
      function: "lambda x: x.title() if x != 'invalid' else 'INVALID'"  # Format
  type: string
```

### Advanced Examples

#### Complex Text Processing
```yaml
text_analysis:
  source: "description"
  operations:
    - type: map
      function: |
        lambda x: {
            'word_count': len(str(x).split()),
            'char_count': len(str(x)),
            'has_numbers': bool(re.search(r'\d', str(x)))
        } if pd.notna(x) else {'word_count': 0, 'char_count': 0, 'has_numbers': False}
    - type: map
      function: "lambda x: f\"Words: {x['word_count']}, Chars: {x['char_count']}, HasNums: {x['has_numbers']}\""
  type: string
```

#### Number Processing
```yaml
parsed_numbers:
  source: "number_list"  # Contains "1,2,3,4,5"
  operations:
    - type: map
      function: "lambda x: [float(n) for n in str(x).split(',') if n.strip()]"
    - type: map
      function: "lambda x: {'sum': sum(x), 'avg': np.mean(x), 'max': max(x)}"
    - type: map  
      function: "lambda x: f\"Sum: {x['sum']:.2f}, Avg: {x['avg']:.2f}, Max: {x['max']:.2f}\""
  type: string
```

### Available Functions in Lambda

Lambda functions have access to:
- **Standard functions**: `str()`, `int()`, `float()`, `len()`, `abs()`, `max()`, `min()`, `round()`
- **Math functions**: All numpy functions via `np.`
- **Pandas functions**: All pandas functions via `pd.`  
- **Regex**: Regular expressions via `re.`
- **Type checking**: `isinstance()`, `type()`
- **Boolean logic**: `and`, `or`, `not`
- **Conditionals**: `if/else` expressions

### Security Notes

- Lambda functions run in a **safe environment** with restricted access
- No access to file system, network, or system functions
- Only whitelisted functions and modules available
- Code is parsed and validated before execution

## Dependency-Aware Processing

DataTidy automatically resolves column dependencies and executes transformations in the correct order, regardless of how you define them in the configuration.

### Column Dependencies

Columns can reference other computed columns, and DataTidy will determine the execution order:

```yaml
output:
  columns:
    # Define in any order - DataTidy resolves dependencies automatically
    final_score:
      transformation: "(profit_score + volume_score) / 2"  # Depends on other columns
      type: float
    
    volume_score:  # This will be calculated before final_score
      transformation: "quantity * 0.1"
      type: float
      interim: true  # Won't appear in final output
    
    profit_score:  # This will also be calculated before final_score
      transformation: "price * quantity * 0.05"
      type: float
      interim: true
```

### Interim Columns

Use interim columns for intermediate calculations that shouldn't appear in the final output:

```yaml
output:
  columns:
    # Interim column - used for calculations but excluded from output
    total_sales:
      transformation: "price * quantity"
      type: float
      interim: true
    
    # Final column - uses interim column
    sales_category:
      transformation: "'high' if total_sales > 1000 else 'low'"
      type: string
```

### Execution Order Resolution

**Automatic Dependency Resolution:**
1. **Parse all expressions** to find column references
2. **Build dependency graph** showing which columns depend on others  
3. **Topological sort** to determine safe execution order
4. **Detect circular dependencies** and throw errors if found
5. **Execute in resolved order** ensuring all dependencies are available

**Example Resolution:**
```yaml
# Configuration (random order)
columns:
  step_3: {transformation: "step_1 + step_2"}  # Depends on step_1, step_2
  step_1: {transformation: "price * 2"}        # Depends on input column
  step_2: {transformation: "quantity * 3"}     # Depends on input column

# Resolved execution order:
# 1. step_1 (depends on: price)
# 2. step_2 (depends on: quantity)  
# 3. step_3 (depends on: step_1, step_2)
```

### Output Control

Control which columns appear in the final result:

```yaml
output:
  only_output_columns: false  # Keep input columns + final output columns (default)
  # only_output_columns: true   # Only include non-interim output columns
  
  columns:
    calculated_field:
      transformation: "price * quantity"
      interim: false  # Will appear in output
    
    temp_calculation:
      transformation: "calculated_field * 0.1"
      interim: true   # Won't appear in output
```

### Advanced Dependency Examples

#### Multi-Level Dependencies
```yaml
output:
  columns:
    # Level 4: Final result
    recommendation:
      transformation: "f'Score: {final_score:.1f}, Action: {action}'"
    
    # Level 3: Business logic
    action:
      transformation: "'promote' if final_score > 8 else 'maintain'"
      interim: true
    
    # Level 2: Combined scoring  
    final_score:
      transformation: "(profit_score + volume_score) / 2"
      interim: true
    
    # Level 1: Base calculations
    profit_score:
      transformation: "revenue * 0.3"
      interim: true
    
    volume_score:
      transformation: "quantity / 10"
      interim: true
    
    revenue:
      transformation: "price * quantity"
      interim: true
```

#### Using Interim Columns in Filters
```yaml
output:
  columns:
    total_value:
      transformation: "price * quantity"
      interim: true  # Used in filter but not in output
    
    product_summary:
      transformation: "f'{product}: ${total_value:.2f}'"
  
  filters:
    - condition: "total_value > 500"  # Filter using interim column
      action: keep
```

### Debugging Dependencies

Enable debugging to see how DataTidy resolves dependencies:

```yaml
global_settings:
  show_execution_plan: true  # Show dependency resolution
  verbose: true              # Show processing progress

# Output will show:
# === EXECUTION PLAN ===
# Total columns to process: 5
# Execution order: revenue -> profit_score -> volume_score -> final_score -> recommendation
# Interim columns: ['revenue', 'profit_score', 'volume_score', 'final_score']
# Final columns: ['recommendation']
# Dependencies:
#   profit_score depends on: revenue
#   volume_score depends on: quantity
#   final_score depends on: profit_score, volume_score
#   recommendation depends on: final_score
```

### Error Handling

**Circular Dependency Detection:**
```yaml
columns:
  col_a: {transformation: "col_c + 1"}  # A depends on C
  col_b: {transformation: "col_a * 2"}  # B depends on A  
  col_c: {transformation: "col_b + 5"}  # C depends on B -> CIRCULAR!

# Error: Circular dependency detected in columns: {'col_a', 'col_b', 'col_c'}
```

**Missing Dependency Detection:**
```yaml
columns:
  result: {transformation: "nonexistent_column * 2"}

# Error: Column 'result': transformation references unknown column 'nonexistent_column'
```

### Filters

Filters remove or keep rows based on conditions.

```yaml
output:
  filters:
    - condition: "age >= 18"
      action: keep
    - condition: "email.find('@') > 0"
      action: keep
    - condition: "status == 'deleted'"
      action: remove
```

#### Filter Properties
- `condition` (required): Python expression returning true/false
- `action` (optional): `"keep"` (default) or `"remove"`

### Sorting

Sort the output data by one or more columns.

```yaml
output:
  sort:
    - column: user_id
      ascending: true
    - column: created_date
      ascending: false
```

#### Sort Properties
- `column` (required): Column name to sort by
- `ascending` (optional): `true` (default) or `false`

## Global Settings

Optional settings that affect the entire processing pipeline.

```yaml
global_settings:
  ignore_errors: false    # Continue processing despite validation errors
  max_errors: 100         # Maximum errors before stopping
  encoding: utf-8         # Default text encoding
```

### Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ignore_errors` | boolean | `false` | Continue processing when validation fails |
| `max_errors` | integer | `100` | Maximum validation errors before stopping |
| `encoding` | string | `"utf-8"` | Default character encoding |

## Complete Example

```yaml
# Complete DataTidy configuration example
input:
  type: csv
  source: "data/users.csv"
  options:
    encoding: utf-8
    delimiter: ","

output:
  columns:
    user_id:
      source: "id"
      type: int
      validation:
        required: true
        min_value: 1

    full_name:
      source: "name"
      type: string
      transformation: "str.strip().title()"
      validation:
        required: true
        min_length: 2
        max_length: 100

    email:
      source: "email_address"
      type: string
      validation:
        required: true
        pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

    age_group:
      transformation: "'senior' if age > 65 else ('adult' if age >= 18 else 'minor')"
      type: string
      validation:
        allowed_values: ["senior", "adult", "minor"]

    signup_date:
      source: "registration_date"
      type: datetime
      format: "%Y-%m-%d"

    is_active:
      source: "status"
      transformation: "status.lower() == 'active'"
      type: bool

  filters:
    - condition: "age >= 0 and age <= 120"
      action: keep
    - condition: "email.find('@') > 0"
      action: keep

  sort:
    - column: user_id
      ascending: true

global_settings:
  ignore_errors: false
  max_errors: 50
  encoding: utf-8
```

## Schema Validation

DataTidy validates your configuration against a JSON schema. Common validation errors include:

- **Missing required fields:** `input` and `output.columns` are required
- **Invalid data types:** Column types must be `string`, `int`, `float`, `bool`, or `datetime`
- **Invalid column names:** Must start with letter/underscore, contain only alphanumeric characters and underscores
- **Invalid source types:** Must be one of the supported input types
- **Invalid validation rules:** Rules must match expected types and formats

## Quick Reference: Join Suffixes

| Scenario | Suffix Config | Left Column | Right Column | Result |
|----------|---------------|-------------|--------------|---------|
| Both have 'name' | `["_L", "_R"]` | name | name | name_L, name_R |
| Keep left unchanged | `["", "_right"]` | name | name | name, name_right |
| Descriptive suffixes | `["_user", "_prod"]` | name | name | name_user, name_prod |
| Default (not specified) | `["_left", "_right"]` | name | name | name_left, name_right |

**Remember:**
- Join keys never get suffixed
- Unique columns keep original names  
- Only conflicting columns get suffixes
- Must specify exactly 2 strings: `[left_suffix, right_suffix]`

## Best Practices

1. **Start simple:** Begin with basic column mappings before adding transformations
2. **Validate early:** Use validation rules to catch data quality issues
3. **Test expressions:** Verify transformation expressions with sample data
4. **Use descriptive suffixes:** `["_customer", "_order"]` instead of `["_left", "_right"]`
5. **Plan column names:** Consider suffix impact when designing transformations
6. **Use comments:** YAML supports comments to document complex configurations
7. **Version control:** Keep configuration files under version control
8. **Secure connections:** Use environment variables for database credentials

## Troubleshooting

### Common Issues

**"Configuration validation error"**
- Check YAML syntax and required fields
- Verify column names are valid identifiers
- Ensure data types are supported

**"Source column not found"**
- Check column names match input data exactly
- Use transformation expressions for computed columns

**"Expression evaluation error"**
- Verify expression syntax and available functions
- Check column references exist in input data
- Test complex expressions incrementally

**"Validation failed"**
- Review validation rules for correctness
- Check if data meets validation criteria
- Consider using `ignore_errors: true` for debugging