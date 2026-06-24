# swe-study-guide

![CI](https://img.shields.io/github/actions/workflow/status/alex3m6/swe-study-guide/ci.yml?branch=main&label=CI)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-95%25-green.svg)

A study guide for software engineering technologies and skills

## Features

- **Technology-organized content** — study notes for FastAPI, Java, and Postgres, each broken into focused topics
- **Concepts + notes per topic** — every topic has a `concepts.md` reference and a personal `notes.md` scratchpad
- **NotebookLM source bundles** — deterministic text-only topic bundles can be generated under `notebooklm/` for study workflows
- **Local study site** — `python serve.py` scans `content/` and serves an interactive frontend at `localhost:8080`
- **Coverage-gated CI** — lint, type check, 95% coverage requirement, and security scanning on every push

## Quick Start

### Prerequisites

- Python 3.12 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/alex3m6/swe-study-guide.git
cd swe-study-guide
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the local study site:
```bash
python serve.py --port 8080
```

### Usage

```bash
# Run the study site
python serve.py --port 8080
```

## Configuration

The study site does not require a runtime config file. Deployment metadata for
`/health` is derived from `src/release_info.py`, and the optional `config/`
files remain available for template scaffolding and future extensions.

```yaml
# Example configuration
app:
  debug: false
  log_level: INFO

# Add your configuration sections here
```

## Project Structure

```
swe-study-guide/
├── .github/workflows/    # CI/CD configuration
├── .claude/              # Claude Code configuration
├── ai-skills/            # Canonical AI skill definitions and helper scripts
├── config/               # Optional template configuration files
├── content/              # Study content rendered by the site
├── docs/                 # Documentation
├── notebooklm/           # Generated text-only NotebookLM source bundles
├── scripts/              # Local automation helpers
├── site/                 # Frontend assets for the study site
├── infra/                # Deployment and skill-render automation
├── src/                  # Shared helpers such as release metadata/logging
├── tests/                # Test files
├── AGENTS.md             # Source-of-truth agent guidance
├── CLAUDE.md             # Symlink to AGENTS.md for Claude compatibility
├── README.md             # This file
├── pyproject.toml        # Tool configuration
└── requirements.txt      # Dependencies
```

## Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
./venv/bin/pytest

# Run with coverage
./venv/bin/pytest --cov=src --cov-report=term-missing
```

### Code Quality

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **bandit** for security scanning
- **pip-audit** for dependency vulnerability checking
- **gitleaks** for secret detection in commits and repository history

Baseline checks run automatically via pre-commit hooks and GitHub Actions.

## CI/CD

GitHub Actions runs the following checks on every push and PR:

1. **Lint**: Black, isort, flake8, mypy
2. **Test**: pytest across Python 3.12
3. **Coverage**: 95% minimum coverage
4. **Security**: bandit and pip-audit
5. **Secret scanning**: gitleaks against repository history with redacted reporting

See [docs/CI.md](docs/CI.md) for details.

## Documentation

- [Documentation Index](docs/INDEX.md) - All documentation
- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [CI Documentation](docs/CI.md) - CI/CD pipeline details
- [Security Baseline](docs/SECURITY_BASELINE.md) - Secret scanning and recommended GitHub security features
- [AI Skills](docs/AI_SKILLS.md) - Canonical AI-skill source and deploy workflow
- [NotebookLM sources](docs/AI_SKILLS.md#study-guide-notebooklm-bundles) - Topic bundle generation for NotebookLM

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE).
