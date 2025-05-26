# Journey

Welcome to the Journey AI Repository! This README.md file will go over how to setup the local development environment.

---

## Prerequisites
* Python 3.10+
* [Poetry](https://python-poetry.org/docs/#installation)
* Docker and Docker Compose

---

## Installation

Run the following command to install the dependencies and create a `.env.local` file.
```bash
make setup-local
```

After setup, external API keys and other unfilled fields must be filled in the generated `.env.local`.

## Running

You can then run `make run-local` to actually run the app locally. The host and port will be `0.0.0.0:8000`.

---

For additional README docs such as developing with the app, check `docs/`.
