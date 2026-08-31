# Contributing to aiogram_tool

First off, thank you for considering contributing to **aiogram_tool**! 🎉
It's people like you that make this project a great toolkit for the [aiogram 3.x](https://github.com/aiogram/aiogram) community.

This document describes how to set up your development environment, run tests, follow the project's code style, and submit changes.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Code Style & Linting](#code-style--linting)
- [Making Changes](#making-changes)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Commit Messages](#commit-messages)
- [Documentation](#documentation)
- [License](#license)

## Ways to Contribute

You can help the project in many ways:

- 🐛 Report bugs
- 💡 Suggest new features or improvements
- 📖 Improve or translate documentation (`docs/en/`, `docs/ru/`)
- ✍️ Write or improve examples in `examples/`
- 🧪 Add tests or increase test coverage
- 🔧 Fix issues and submit pull requests

## Reporting Bugs

Before opening a bug report, please [search existing issues](https://github.com/shayzi3/aiotool/issues) to avoid duplicates.

When creating a bug report, include:

- A clear, descriptive title
- Your Python version, aiogram version, and `aiogram_tool` version
- Steps to reproduce the problem (a minimal code example is best)
- Expected behavior vs. actual behavior
- Full traceback, if applicable

## Suggesting Enhancements

Feature requests are welcome! Please open an issue and describe:

- The problem you're trying to solve
- Your proposed solution or API design
- Any alternatives you've considered
- Whether it fits the scope of the project (tools and utilities for aiogram 3.x)

## Development Setup

### Prerequisites

- **Python 3.11+**
- [**uv**](https://docs.astral.sh/uv/) — the package manager used by this project
- **Git**
- **Redis** (optional, but recommended — some tests use a Redis backend)

### Getting Started

1. Fork the repository and clone your fork:

   ```bash
   git clone https://github.com/<your-username>/aiotool.git
   cd aiotool
   ```

2. Install dependencies (including dev tools):

   ```bash
   uv sync --all-extras --dev
   ```

3. Install the pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

   This ensures `ruff check --fix` and `ruff format` run automatically before each commit.

## Project Structure

```
aiogram_tool/
├── aiogram_tool/          # Main package source code
│   ├── types.py           # Shared type definitions
│   ├── storage/           # Storage backends (Memory, Redis, File)
│   └── tools/             # Tools (depend, limit, callback_data, setup)
├── docs/                  # Documentation (en/ and ru/)
├── examples/              # Ready-to-run usage examples
├── tests/                 # Test suite (pytest)
├── pyproject.toml         # Project metadata and tool configuration
└── .pre-commit-config.yaml
```

## Running Tests

The test suite uses [pytest](https://docs.pytest.org/) with `pytest-asyncio` (asyncio mode is set to `auto`).

```bash
uv run pytest
```

Notes:

- Some tests require a **Redis** instance available at `localhost:6379`. In CI, a Redis 7 service container is started automatically. Locally, you can run one with Docker:

  ```bash
  docker run -d -p 6379:6379 redis:7-alpine
  ```

- To run a specific test module or directory:

  ```bash
  uv run pytest tests/limit/
  ```

When adding new features, please add corresponding tests under `tests/`, mirroring the package structure.

## Code Style & Linting

This project uses [**ruff**](https://docs.astral.sh/ruff/) for both linting and formatting.

Configuration highlights (see `pyproject.toml`):

- Line length: **88**
- Target version: **Python 3.11**
- Quote style: **double quotes**
- Enabled rule sets: `E4`, `E7`, `E9`, `F`, `I` (isort), `B` (bugbear), `UP` (pyupgrade)

Run the linter and formatter manually:

```bash
uv run ruff check --fix
uv run ruff format
```

Or verify without modifying files (as CI does):

```bash
uv run ruff check
uv run ruff format --check
```

CI runs both a **test job** (Python 3.11 and 3.12) and a **lint job**, so please make sure both pass locally before opening a pull request.

## Making Changes

1. Create a new branch for your work:

   ```bash
   git checkout -b feature/my-feature
   # or
   git checkout -b fix/issue-123
   ```

2. Make your changes.
3. Add or update tests for your changes.
4. Update documentation (`docs/en/` and `docs/ru/`) and, if relevant, add an example in `examples/`.
5. Run the linter, formatter, and tests:

   ```bash
   uv run ruff check
   uv run ruff format --check
   uv run pytest
   ```

6. Commit your changes (pre-commit hooks will run automatically) and push your branch.
7. Open a pull request against the `master` branch.

## Pull Request Guidelines

- Keep pull requests focused — one feature or fix per PR.
- Describe **what** you changed and **why**.
- Reference related issues (e.g., `Fixes #123`).
- Make sure all CI checks pass.
- New public APIs should be documented and covered by tests.
- Follow the existing code style and project structure.

## Commit Messages

Write clear, concise commit messages. We recommend the [Conventional Commits](https://www.conventionalcommits.org/) style:

```
feat: add token bucket rate limit option
fix: handle empty callback data in LongCallbackData
docs: update rate limiter documentation
test: add tests for Redis storage backend
refactor: simplify dependency resolution logic
```

## Documentation

Documentation lives in `docs/` and is available in two languages:

- `docs/en/` — English
- `docs/ru/` — Russian

If you add or change a feature, please update the documentation in **both** languages when possible. Runnable examples belong in `examples/`, organized by tool.

## License

By contributing to `aiogram_tool`, you agree that your contributions will be licensed under the same license as the project — see [LICENSE.md](LICENSE.md).

---

Thank you again for contributing! 💙