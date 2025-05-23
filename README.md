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

To start the application, use the following command:

```bash
honcho -e {env_file} start
```

Replace `{env_file}` with the path to your `.env` file.

---

## Managing Workers

Workers are managed through the `Procfile` and will run automatically when you start the application with `honcho`. If you need to add new workers, ensure they are added to the `Procfile`.

---
