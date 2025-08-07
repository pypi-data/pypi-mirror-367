<div align="center">
  <img src="https://gitlab.com/Shacode/decoguard/-/raw/main/docs/logo.png" alt="decoguard logo" width="250">
</div>

# 🛡️ DECOGUARD
[![Latest Release](https://gitlab.com/Shacode/decoguard/-/badges/release.svg)](https://gitlab.com/Shacode/decoguard/-/releases)
[![Pipeline Status](https://gitlab.com/Shacode/decoguard/badges/main/pipeline.svg)](https://gitlab.com/Shacode/decoguard/-/pipelines)
[![Coverage Report](https://gitlab.com/Shacode/decoguard/badges/main/coverage.svg)](https://gitlab.com/Shacode/decoguard/-/jobs)
[![Documentation](https://img.shields.io/badge/View%20Docs-online-blue?logo=readthedocs)](https://decoguard.readthedocs.io/en/latest/)
[![AGPL v3 License](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python)](https://www.python.org/)
[![Made with Love](https://img.shields.io/badge/Made%20with-%E2%9D%A4-blue)](https://gitlab.com/Shacode/decoguard)

Lightweight Python library for robustly validating decorated functions, providing a clean, structured way to ensure they comply with defined conditions.

[📚 The complete documentation is available here.](https://decoguard.readthedocs.io/en/latest/)

## ✨ Features

- **Meta-Decorators**: Easily add validation logic to your decorators and decorator factories.
- **Validator Functions**: Fine-grained validation rules for function signatures and usage.
- **Assertion Utilities**: Reusable assertion helpers for standalone validation.
- **Centralized Validation**: Keep your validation logic clean and maintainable.
- **Clear Error Reporting**: Developer-friendly exceptions for invalid decorator usage.
- **Drop-In Simplicity**: Integrate with existing Python code with minimal changes.

## 🚀 Getting Started

1. **Install decoguard**
   ```bash
   pip install decoguard
   ```
2. **Import and use meta-decorators**
   ```python
   from decoguard.decorators import validate_decorated
   from decoguard.validators import require_params

   @validate_decorated(require_params("x", "y"))
   def my_decorator(func): return func

   @my_decorator
   def correct_usage(x, y): pass

   @my_decorator
   def bad_usage(x): pass # Will raise DecoratorUsageValidationError
   ```

## 💚 CI/CD Pipeline

This project maintains high code quality through automated GitLab CI/CD pipelines that run on every merge request and main branch commit:

### Quality Assurance
- **Code Testing**: Comprehensive test suite using `tox` and `pytest` with coverage reporting
- **Code Formatting**: Automated formatting with `black` and import sorting with `isort`
- **Code Style**: Style checking with `flake8` following project standards
- **Type Checking**: Static type analysis using `mypy` for type safety
- **Security Scanning**:
  - Dependency vulnerability checks with `safety`
  - Code security analysis with `bandit` (excluding test files)

### Deployment
- **Automated Building**: Package building and integrity validation
- **PyPI Deployment**: Automatic deployment to PyPI on tagged releases
- **Manual Release**: Production deployments require manual approval for safety

The same quality checks can be run locally using the included `format_and_check.py` script.

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0. See [LICENSE](LICENSE) for details.
