# Contributing to DataTidy

Thank you for your interest in contributing to DataTidy! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/datatidy.git
   cd datatidy
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to ensure everything works**
   ```bash
   pytest tests/ -v
   ```

## 🧪 Development Workflow

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=datatidy --cov-report=html

# Run specific test file
pytest tests/test_core.py -v
```

### Code Quality Checks
```bash
# Format code with black
black datatidy/ tests/

# Lint with flake8
flake8 datatidy/ tests/

# Type check with mypy
mypy datatidy/ --ignore-missing-imports
```

### Testing Your Changes
```bash
# Test package installation
pip install -e .

# Test CLI commands
datatidy sample test_config.yaml
datatidy validate test_config.yaml
```

## 📝 Contributing Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use Black for code formatting (`black .`)
- Maximum line length: 88 characters
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Commit Messages
- Use clear, descriptive commit messages
- Start with a verb in present tense
- Reference issues when applicable
- Examples:
  - `Add support for Parquet file input`
  - `Fix dependency resolution for circular references`
  - `Update documentation for join operations`

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Submit pull request**
   - Provide clear description of changes
   - Reference any related issues
   - Include examples if adding new features

### What to Contribute

#### 🐛 Bug Fixes
- Fix reported issues
- Add regression tests
- Update documentation if needed

#### ✨ New Features
- New input/output formats
- Additional transformation operations
- Enhanced validation rules
- Performance improvements

#### 📚 Documentation
- Improve existing documentation
- Add examples and tutorials
- Fix typos and clarifications

#### 🧪 Tests
- Increase test coverage
- Add edge case testing
- Performance benchmarks

## 🏗️ Project Structure

```
datatidy/
├── datatidy/           # Main package
│   ├── config/         # Configuration parsing
│   ├── input/          # Data readers
│   ├── transformation/ # Processing engine
│   ├── cli.py         # Command-line interface
│   └── core.py        # Main DataTidy class
├── tests/             # Test suite
├── examples/          # Example configurations
├── docs/              # Documentation
└── assets/            # Logos and images
```

## 🔧 Adding New Features

### Adding a New Input Source
1. Create reader class in `datatidy/input/readers.py`
2. Add to `DataReaderFactory`
3. Update configuration schema
4. Add tests and examples

### Adding New Operations
1. Create operation class in `datatidy/transformation/column_operations.py`
2. Register in operation factory
3. Update dependency analysis if needed
4. Add comprehensive tests

### Adding Validation Rules
1. Extend validation in `datatidy/transformation/engine.py`
2. Update schema in `datatidy/config/schema.py`
3. Add test cases for edge cases

## 📋 Issue Guidelines

### Reporting Bugs
- Use the bug report template
- Include Python version and OS
- Provide minimal reproduction example
- Include full error traceback

### Feature Requests
- Use the feature request template
- Explain the use case clearly
- Provide examples of desired behavior
- Discuss implementation approach

### Questions and Support
- Check existing documentation first
- Search closed issues for solutions
- Use GitHub Discussions for questions
- Provide context and examples

## 🧪 Testing Guidelines

### Test Coverage
- Maintain >90% test coverage
- Test both success and failure cases
- Include edge cases and boundary conditions
- Test CLI commands and configuration parsing

### Test Organization
```
tests/
├── test_core.py              # Core functionality
├── test_config_parser.py     # Configuration parsing
├── test_readers.py           # Input readers
├── test_transformation_engine.py  # Processing
├── test_expressions.py       # Expression evaluation
└── fixtures/                 # Test data files
```

### Writing Tests
```python
def test_feature_name():
    """Test description of what is being tested."""
    # Arrange
    input_data = create_test_data()
    config = create_test_config()
    
    # Act
    result = process_data(input_data, config)
    
    # Assert
    assert result.shape[0] == expected_rows
    assert "new_column" in result.columns
```

## 🚀 Release Process

### Version Numbering
- Follow Semantic Versioning (SemVer)
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Release Checklist
1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Create GitHub release
5. Automated PyPI publication via GitHub Actions

## 💬 Community

### Getting Help
- GitHub Discussions for questions
- GitHub Issues for bugs and features
- Check documentation and examples first

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and contribute
- Follow GitHub's community guidelines

## 🙏 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor statistics

Thank you for contributing to DataTidy! 🎉