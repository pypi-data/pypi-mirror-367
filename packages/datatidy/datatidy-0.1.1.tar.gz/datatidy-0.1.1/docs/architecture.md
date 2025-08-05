# DataTidy Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    DataTidy                                     │
│                         Configuration-Driven Data Processing                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Layer   │    │ Config Layer    │    │Transform Layer  │    │  Output Layer   │
│                 │    │                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   CSV       │ │    │ │    YAML     │ │    │ │ Expression  │ │    │ │    CSV      │ │
│ │   Files     │ │────┤ │   Parser    │ │────┤ │   Parser    │ │────┤ │   Files     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Excel     │ │    │ │   Schema    │ │    │ │Transformation│ │    │ │   Excel     │ │
│ │   Files     │ │    │ │ Validator   │ │    │ │   Engine    │ │    │ │   Files     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │    │                 │
│ ┌─────────────┐ │    │                 │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Databases   │ │    │                 │    │ │ Data        │ │    │ │   JSON      │ │
│ │(Snowflake,  │ │    │                 │    │ │ Validator   │ │    │ │   Files     │ │
│ │PostgreSQL,  │ │    │                 │    │ └─────────────┘ │    │ └─────────────┘ │
│ │MySQL, etc.) │ │    │                 │    │                 │    │                 │
│ └─────────────┘ │    │                 │    │                 │    │ ┌─────────────┐ │
│                 │    │                 │    │                 │    │ │  Parquet    │ │
│ ┌─────────────┐ │    │                 │    │                 │    │ │   Files     │ │
│ │  Pandas     │ │    │                 │    │                 │    │ └─────────────┘ │
│ │ DataFrame   │ │    │                 │    │                 │    │                 │
│ └─────────────┘ │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Configuration Flow

```
┌─────────────┐
│ YAML Config │
│    File     │
└──────┬──────┘
       │
       ▼
┌─────────────┐       ┌─────────────┐
│   Config    │──────▶│   Schema    │
│   Parser    │       │ Validator   │
└──────┬──────┘       └─────────────┘
       │
       ▼
┌─────────────┐
│ Normalized  │
│   Config    │
│ Dictionary  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Transformation│
│   Engine    │
└─────────────┘
```

## Data Processing Pipeline

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Raw Data  │    │   Column    │    │   Data      │    │  Validated  │
│   Sources   │───▶│ Mapping &   │───▶│ Type Conv.  │───▶│    Data     │
│             │    │Transform.   │    │& Formatting │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Final     │    │   Sorted    │    │  Filtered   │    │ Validation  │
│   Output    │◀───│    Data     │◀───│    Data     │◀───│   Rules     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Configuration Structure

```yaml
input:                          # Input source definition
  type: csv|excel|database      # Source type
  source: "path/to/file"        # File path or query
  connection_string: "..."      # For databases
  options: {}                   # Reader-specific options

output:                         # Output specification
  columns:                      # Column definitions
    column_name:
      source: "source_col"      # Maps to: table.column or expression
      type: string              # Data type: string, int, float, bool, datetime
      format: "YYYY-MM-DD"      # Format specification
      transformation: |         # Complex transformation logic
        'adult' if age >= 18 else 'minor'
      validation:               # Validation rules
        required: true
        nullable: false
        min_value: 0
        max_value: 100
        min_length: 2
        max_length: 50
        pattern: "^[A-Za-z]+$"
        allowed_values: ["A", "B", "C"]
      default: "N/A"           # Default value

  filters:                      # Row filtering
    - condition: "age >= 18"
      action: keep

  sort:                         # Result sorting
    - column: "user_id"
      ascending: true

global_settings:                # Global processing settings
  ignore_errors: false
  max_errors: 100
  encoding: "utf-8"
```

## Expression System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Safe Expression Parser                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Supported Operations:                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Arithmetic  │ │ Comparison  │ │   Logical   │ │   String    │              │
│  │  +, -, *,   │ │ ==, !=, <,  │ │ and, or,    │ │   Methods   │              │
│  │  /, //, %   │ │ <=, >, >=   │ │    not      │ │             │              │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                                 │
│  Column References:           Functions:              Literals:                 │
│  ┌─────────────┐              ┌─────────────┐       ┌─────────────┐            │
│  │ column_name │              │ str(), int()│       │ 'string',   │            │
│  │ table.col   │              │ max(), min()│       │ 123, 45.6,  │            │
│  └─────────────┘              │ len(), abs()│       │ True, False │            │
│                               └─────────────┘       └─────────────┘            │
│                                                                                 │
│  Conditional Expressions:                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 'adult' if age >= 18 else 'minor'                                      │   │
│  │ 'high' if score > 80 else ('medium' if score > 60 else 'low')          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Class Hierarchy

```
DataTidy (Main Interface)
├── ConfigParser (YAML Processing)
│   └── ConfigSchema (JSON Schema Validation)
├── DataReaderFactory (Input Abstraction)
│   ├── CSVReader
│   ├── ExcelReader
│   └── DatabaseReader
└── TransformationEngine (Core Processing)
    ├── ExpressionParser (Safe Expression Evaluation)
    │   └── SafeExpressionParser (AST-based Security)
    └── ValidationError (Error Handling)
```

## Security Features

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Security Layers                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  AST-Based Expression Parsing                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • Only safe operations allowed                                          │   │
│  │ • No arbitrary code execution                                           │   │
│  │ • Whitelist of allowed functions                                        │   │
│  │ • No access to system functions                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  Configuration Validation                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • JSON Schema validation                                                │   │
│  │ • Type checking                                                         │   │
│  │ • Required field validation                                             │   │
│  │ • Pattern matching for formats                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  Error Handling                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ • Controlled error propagation                                          │   │
│  │ • Maximum error limits                                                  │   │
│  │ • Graceful degradation options                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```