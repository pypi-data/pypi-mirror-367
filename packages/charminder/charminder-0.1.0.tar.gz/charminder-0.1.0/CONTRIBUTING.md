# Contributing

Thank you for your interest in contributing to CharMinder! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- Git

### Setting Up Your Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/charminder.git
   cd charminder
   ```

3. Create a virtual environment and install dependencies using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install the package in development mode:
   ```bash
   uv pip install -e .
   ```

## How to Contribute

### Reporting Issues

Before creating an issue, please:
- Check if the issue already exists in the GitHub issues
- Provide clear steps to reproduce the problem
- Include your Python version and operating system
- Include sample files or URLs that demonstrate the issue

### Submitting Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test them thoroughly

3. Commit your changes with a clear commit message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

4. Push to your fork and submit a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Guidelines

- Keep pull requests focused on a single issue or feature
- Write clear, descriptive commit messages
- Include tests for new functionality
- Update documentation as needed
- Follow the existing code style

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to new functions and classes
- Keep functions focused and reasonably sized

## Testing

Before submitting a pull request:
- Test your changes with various file types and encodings
- Verify that existing functionality still works
- Test both local files and remote URLs

## License

By contributing to CharMinder, you agree that your contributions will be licensed under the Apache License, Version 2.0.

## Questions?

If you have questions about contributing, feel free to:
- Open an issue for discussion
- Reach out to the maintainers

We appreciate all contributions, whether they're bug reports, feature requests, documentation improvements, or code changes!

