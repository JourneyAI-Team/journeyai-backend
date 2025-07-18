# JourneyAI Local Development Setup (MacOS)

Poetry is the package manager

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.10+](https://www.python.org/downloads/)
- [Homebrew](https://brew.sh/) or [PIP](https://pip.pypa.io/en/stable/installation/)

## Installation

1. Install Poetry and run Makefile
```bash
brew install poetry # or pipx install poetry
make setup-local
```
2. Add keys to .env.local file, especially `OPENAI_API_KEY`

**Note**: Tempting as it us, use `poetry` for dependency management rather than homebrew. Otherwise, `poetry` will attempt to use system-level packages, which may lead to conflicts or unexpected behavior.

## Running

Revert back to [README.md](../README.md)
