# IAM Policy Lint

A comprehensive tool for linting and validating AWS IAM (Identity and Access Management) policies in JSON, YAML, and embedded formats. Built around the powerful [Parliament](https://github.com/duo-labs/parliament) library, this tool helps you identify security issues, policy problems, and structural errors in your IAM policies.

## Features

- 🔍 **Deep Policy Analysis**: Uses Parliament to detect security issues and policy problems
- 📝 **Structure Validation**: Validates basic IAM policy structure and syntax
- 🔧 **Multiple Formats**: Supports JSON and YAML IAM policies, plus embedded policies in YAML
- 🎯 **Embedded Policy Support**: Extract and lint IAM policies embedded in Kubernetes manifests, Terraform, CloudFormation, etc.
- 📁 **Directory Scanning**: Lint all policies in a directory at once
- 🎯 **Severity Filtering**: Filter findings by severity level (CRITICAL, HIGH, MEDIUM, LOW)
- 📊 **Multiple Output Formats**: Human-readable text or machine-readable JSON output
- 🖥️ **CLI Interface**: Easy-to-use command-line interface
- 🔗 **Pre-commit Integration**: Automated policy checking in Git workflows

## Installation

### Prerequisites

- Python 3.12+
- pyenv (recommended for Python version management)
- uv (for package management)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/iam-policy-lint.git
   cd iam-policy-lint
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
iam-policy-lint lint examples/policy.json

# Lint a YAML policy
iam-policy-lint lint examples/policy.yaml

# With severity filtering and JSON output
iam-policy-lint lint examples/policy.json --severity HIGH --format json
```

#### Validate policy structure

```bash
# Basic structure validation
iam-policy-lint validate examples/policy.json

# Validation with JSON output
iam-policy-lint validate examples/policy.json --format json
```

#### Lint directory of policies

```bash
# Lint all policies in a directory
iam-policy-lint lint-dir examples/

# With file pattern and severity filtering
iam-policy-lint lint-dir examples/ --pattern "*.yaml" --severity MEDIUM

# Directory linting with JSON output
iam-policy-lint lint-dir examples/ --format json
```

#### Lint embedded policies in YAML files

```bash
# Lint policies embedded in Kubernetes manifests, Terraform, CloudFormation, etc.
iam-policy-lint lint-embedded examples/kubernetes-manifest.yaml

# Lint with custom key path
iam-policy-lint lint-embedded examples/terraform.yaml --key-path "data.policy_document"

# Lint with multiple key paths
iam-policy-lint lint-embedded examples/config.yaml \
  --key-path "spec.policies[].document" \
  --key-path "metadata.annotations.\"iam.policy\""

# Only show critical issues
iam-policy-lint lint-embedded examples/manifest.yaml --severity CRITICAL
```

**Example YAML with embedded IAM policy:**
```yaml
# Kubernetes ServiceAccount with IAM policy annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  annotations:
    "iam.policy": |
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": ["s3:GetObject"],
            "Resource": "arn:aws:s3:::my-bucket/*"
          }
        ]
      }
```

### Python API

```python
from iam_policy_lint import IAMLinter, IAMValidator

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

# Lint embedded policies from YAML
embedded_findings = linter.lint_embedded_policies("path/to/manifest.yaml")
for finding in embedded_findings:
    print(f"Embedded policy issue: {finding['title']}")
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
uv run pytest --cov=src/iam_policy_lint

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
