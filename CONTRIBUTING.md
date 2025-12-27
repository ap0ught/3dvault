# Contributing to 3D Vault

Thank you for your interest in contributing to 3D Vault! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/3dvault.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Make your changes
7. Run tests: `python manage.py test vault.tests -v 2`
8. Commit your changes with a descriptive message
9. Push to your fork: `git push origin feature/your-feature-name`
10. Open a Pull Request

## Code Quality Standards

### Python Style Guide
- Follow **PEP 8** for code style
- Use **PEP 257** for docstrings (all public functions, classes, and modules)
- Apply **PEP 484** type hints throughout
- Keep code clean, tested, and production-ready

### Testing
- All new features must include tests
- Maintain or improve code coverage
- Tests should be in the `vault/tests/` directory
- Run tests before submitting: `python manage.py test vault.tests -v 2`

### Documentation
- Update README.md for user-facing changes
- Add docstrings to all public functions
- Include type hints for all function parameters and return values
- Document "why" not "what" in comments

## Branch Protection and CI/CD

The `main` branch is protected with the following rules:

### Required Status Checks
Before a pull request can be merged to `main`, the following checks must pass:
- **CI**: Automated test suite must pass
- **Lint**: Code quality checks must pass

### Enabling Branch Protection (Admin Only)

For detailed instructions on configuring branch protection, see [BRANCH_PROTECTION.md](.github/BRANCH_PROTECTION.md).

**Quick Summary:**
- Require pull request reviews before merging
- Require status checks to pass (CI + Lint)
- Prevent force pushes to `main`
- Prevent branch deletion of `main`

## Code Review Process

### For Contributors
- Ensure all CI checks pass
- Address all review comments
- Keep pull requests focused and atomic
- Write clear commit messages

### For Reviewers
- Check code quality and adherence to style guide
- Verify tests are included and passing
- Ensure documentation is updated
- Test the changes locally if needed

## Security

- Never commit secrets or credentials
- Follow the security best practices outlined in README.md
- Report security vulnerabilities privately to the maintainers
- All imports are logged in the audit trail (UserHistory)

## Pull Request Template

When creating a pull request, include:
- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was this tested?
- **Related Issues**: Link to related issues

## Questions?

If you have questions or need help, please:
- Check the README.md for documentation
- Review existing issues and pull requests
- Open a new issue for discussion

Thank you for contributing to 3D Vault! 🚀
