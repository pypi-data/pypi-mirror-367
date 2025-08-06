# IAM JSON Lint

A comprehensive tool for linting and validating AWS IAM (Identity and Access Management) policies. Built around the powerful [Parliament](https://github.com/duo-labs/parliament) library, this tool helps you identify security issues, policy problems, and structural errors in your IAM policies.

## Features

- 🔍 **Deep Policy Analysis**: Uses Parliament to detect security issues and policy problems
- 📝 **Structure Validation**: Validates basic IAM policy structure and syntax
- 🔧 **Multiple Formats**: Supports both JSON and YAML IAM policies
- 📁 **Directory Scanning**: Lint all policies in a directory at once
- 🎯 **Severity Filtering**: Filter findings by severity level (HIGH, MEDIUM, LOW)
- 📊 **Multiple Output Formats**: Human-readable text or machine-readable JSON output
- 🖥️ **CLI Interface**: Easy-to-use command-line interface

## Installation

### Prerequisites

- Python 3.12+
- pyenv (recommended for Python version management)
- uv (for package management)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/iam-json-lint.git
   cd iam-json-lint
   ```

2. **Set Python version** (if using pyenv):
   ```bash
   pyenv local 3.12
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Install the package** (for development):
   ```bash
   uv pip install -e .
   ```

## Usage

### Command Line Interface

#### Lint a single policy file

```bash
# Lint a JSON policy file
iam-json-lint lint examples/policy.json

# Lint a YAML policy file  
iam-json-lint lint examples/policy.yaml

# Filter by severity and output as JSON
iam-json-lint lint examples/policy.json --severity HIGH --format json
```

#### Validate policy structure

```bash
# Basic structure validation
iam-json-lint validate examples/policy.json

# Validation with JSON output
iam-json-lint validate examples/policy.json --format json
```

#### Lint directory of policies

```bash
# Lint all JSON files in a directory
iam-json-lint lint-dir examples/

# Lint YAML files with severity filtering
iam-json-lint lint-dir examples/ --pattern "*.yaml" --severity MEDIUM

# Output results as JSON
iam-json-lint lint-dir examples/ --format json
```

### Python API

```python
from iam_json_lint import IAMLinter, IAMValidator

# Initialize linter and validator
linter = IAMLinter()
validator = IAMValidator()

# Lint a policy file
findings = linter.lint_file("path/to/policy.json")
for finding in findings:
    print(f"{finding['severity']}: {finding['title']}")

# Validate policy structure
errors = validator.validate_file("path/to/policy.json")
for error in errors:
    print(f"{error['severity']}: {error['message']}")

# Lint a policy dictionary directly
policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": "*",
        "Resource": "*"
    }]
}

findings = linter.lint_policy(policy)
validation_errors = validator.validate_policy(policy)
```

## Example Output

### Text Output (Default)

```
🔍 Linting results for: examples/overly-permissive.json
============================================================

🔴 Issue #1 - HIGH
Title: Wildcard action
Issue: WILDCARD_ACTION
Description: Action contains a wildcard that allows all actions
Location: Statement[0].Action

🔴 Issue #2 - HIGH  
Title: Wildcard resource
Issue: WILDCARD_RESOURCE
Description: Resource contains a wildcard that allows access to all resources
Location: Statement[0].Resource
```

### JSON Output

```json
[
  {
    "issue": "WILDCARD_ACTION",
    "title": "Wildcard action", 
    "description": "Action contains a wildcard that allows all actions",
    "severity": "HIGH",
    "location": "Statement[0].Action",
    "detail": null
  }
]
```

## Policy Examples

The `examples/` directory contains sample IAM policies:

- `valid-policy.json` - A well-structured policy with specific permissions
- `overly-permissive.json` - A policy with security issues (wildcards)
- `policy.yaml` - A YAML-formatted policy
- `invalid-policy.json` - A structurally invalid policy

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/iam_json_lint

# Run specific test file
uv run pytest tests/test_validator.py
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run flake8 src/ tests/

# Type checking
uv run mypy src/
```

### Project Structure

```
iam-json-lint/
├── src/iam_json_lint/          # Main package
│   ├── __init__.py             # Package initialization
│   ├── linter.py               # Parliament-based linting
│   ├── validator.py            # Basic structure validation
│   └── cli.py                  # Command-line interface
├── tests/                      # Unit tests
├── examples/                   # Sample IAM policies
├── .github/                    # GitHub configuration
│   └── copilot-instructions.md # Copilot instructions
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Dependencies

### Core Dependencies
- **[Parliament](https://github.com/duo-labs/parliament)** - AWS IAM linting library
- **[PyYAML](https://github.com/yaml/pyyaml)** - YAML parser
- **[Click](https://github.com/pallets/click)** - CLI framework

### Development Dependencies
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatter
- **flake8** - Linter
- **mypy** - Type checker

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [Parliament](https://github.com/duo-labs/parliament) by Duo Labs for the core IAM policy analysis engine
- [AWS IAM Policy Reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html) for policy structure guidelines
