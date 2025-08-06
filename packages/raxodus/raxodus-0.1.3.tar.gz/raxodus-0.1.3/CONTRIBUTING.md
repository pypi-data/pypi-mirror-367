# Contributing to Raxodus

First off, thank you for considering contributing to Raxodus! It's people like you that help make this tool better for everyone stuck dealing with Rackspace's API.

## Code of Conduct

By participating in this project, you agree to abide by our simple rule: **Be excellent to each other**. 

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples** (commands, error messages, etc.)
* **Describe the behavior you observed and what you expected**
* **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

* **Use a clear and descriptive title**
* **Provide a step-by-step description** of the suggested enhancement
* **Provide specific examples** to demonstrate the steps
* **Describe the current behavior** and **explain the expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes (`mise run test`)
4. Make sure your code follows the existing style
5. Issue that pull request!

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/raxodus
cd raxodus

# Install mise (if you haven't already)
curl https://mise.run | sh

# Setup development environment
mise run up

# Run tests
mise run test
```

## Development Workflow

We use mise for task automation. Key commands:

```bash
mise run build      # Build the package
mise run test-cli   # Test CLI commands
mise run test       # Run all tests
mise run clean      # Clean build artifacts
```

## Code Style

* We use Python 3.10+ features
* Follow PEP 8
* Use type hints where appropriate
* Keep it simple and readable

## Testing

* Write tests for new features
* Ensure all tests pass before submitting PR
* Test against real Rackspace API when possible (with test account)

## Documentation

* Update README.md if you change functionality
* Add docstrings to new functions/classes
* Update CLI help text for new commands

## Release Process

We follow [Semantic Versioning](https://semver.org/) and use Ultima III themed release names:

* MAJOR.MINOR.PATCH (e.g., 0.1.1)
* Release names from Ultima III characters
* Each release gets a unique DiceBear avatar

## Dealing with Rackspace API Issues

As you've probably noticed, the Rackspace API has... issues. When contributing:

* Document any new API quirks you discover
* Add to `docs/RACKSPACE_API_ISSUES.md` if you find new problems
* Be defensive in your code - assume the API will do weird things
* Add retries and timeouts generously

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

## Recognition

Contributors will be acknowledged in our RELEASES.md file. Your efforts to escape from Rackspace ticket hell are appreciated!

---

Remember: We're all in this together, trying to make the best of a challenging API. Every contribution, no matter how small, helps!