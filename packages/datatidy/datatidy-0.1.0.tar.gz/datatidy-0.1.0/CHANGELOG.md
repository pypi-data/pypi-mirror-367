# Changelog

All notable changes to DataTidy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-01-29

### 🐛 Bug Fixes
- **Logo Visibility**: Created simplified logo for better PyPI page display
- **Project Links**: Fixed incorrect "example" placeholder URLs in package metadata
- **Documentation**: Updated links to point to correct repository structure

### 🎨 Improvements
- **PyPI Logo**: Optimized logo design (300x60px) for better visibility on package pages
- **Icon Design**: Simplified geometric icon design for cleaner display at small sizes
- **Metadata**: Corrected all project URLs to use proper GitHub organization structure

---

## [1.0.0] - 2025-01-29

### 🎉 Initial Release

#### Added
- **Core Features**
  - Configuration-driven data processing with YAML
  - Multiple input sources: CSV, Excel, databases (PostgreSQL, MySQL, Snowflake), Parquet, Pickle
  - Safe expression evaluation with security restrictions
  - Comprehensive data validation and error reporting
  - Command-line interface for batch processing

- **Multi-Input Processing**
  - Support for multiple data sources in single configuration
  - Flexible join operations (inner, left, right, outer, cross)
  - Configurable column suffix handling for joins
  - Factory pattern for extensible data readers

- **Advanced Transformations**
  - Map, reduce, filter, and window operations with lambda functions
  - Chained operations for complex data processing pipelines
  - Source column mapping and type conversions
  - Conditional transformations with safe expression parsing

- **Dependency-Aware Processing**
  - Automatic execution order resolution using topological sorting
  - Interim columns for intermediate calculations
  - Circular dependency detection and error reporting
  - Execution plan visualization and debugging

- **Time Series Support**
  - Lag operations using pandas shift() function
  - Rolling window calculations with lag values
  - Multi-timeframe analysis patterns
  - Trading signal generation examples

- **Configuration System**
  - JSON Schema validation for configurations
  - Comprehensive error messages and validation feedback
  - Global settings for error handling and verbosity
  - Extensible schema for new features

- **Documentation & Examples**
  - Complete configuration reference documentation
  - 20+ example configurations covering all features
  - Python usage examples and tutorials
  - Architecture documentation and design patterns

- **Developer Tools**
  - Unit test suite with >90% coverage
  - CLI commands for validation and sample generation
  - Detailed logging and error reporting
  - Professional packaging for PyPI distribution

#### Security
- AST-based expression parsing with whitelist security
- Restricted function and operator access
- Safe evaluation environment for transformations
- No file system or network access from expressions

#### Performance
- Vectorized operations using pandas
- Efficient dependency resolution algorithms
- Minimal memory overhead for large datasets
- Optimized expression parsing and evaluation

---

## Development Roadmap

### Planned for v1.1.0
- **Enhanced Input Sources**
  - Apache Arrow/Feather format support
  - Cloud storage integration (S3, GCS, Azure Blob)
  - API data sources with authentication
  - Streaming data processing capabilities

- **Advanced Operations**
  - Machine learning transformations integration
  - Statistical operations and aggregations
  - Data profiling and quality assessment
  - Custom operation plugins

- **Performance Improvements**
  - Parallel processing for large datasets
  - Memory optimization for big data
  - Caching mechanisms for repeated operations
  - Incremental processing support

### Planned for v1.2.0
- **Monitoring & Observability**
  - Processing metrics and performance monitoring
  - Data lineage tracking
  - Operation timing and resource usage
  - Integration with monitoring systems

- **Enterprise Features**
  - Role-based access control for configurations
  - Audit logging for data processing
  - Enterprise database support
  - Configuration versioning and management

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to DataTidy.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.