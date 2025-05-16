# Journey

Welcome to the Journey AI Repository!

---

## Prerequisites
* Python 3.10+
* [Poetry](https://python-poetry.org/docs/#installation)

---

## Installation

```bash
poetry install
```

---

## Environment variables

The application expects a `.env` file in the project root.

1. Open the **Journey** vault in 1Password.  
2. Copy the note that contains the `.env` contents.  
3. Create a file named `.env` in the project root and paste the copied text.

---

## Running the application locally

```bash
poetry run python -m app.main
```

test push