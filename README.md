# JourneyAI

JourneyAI is an advanced AI platform focused on enhancing sales processes. It offers ChatGPT-like capabilities with additional features tailored for sales teams.

## Features

- Intelligent sales conversation assistant
- Contextual customer interaction memory
- Sales-specific knowledge base integration
- Task automation and scheduling
- Analytics and reporting

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **Beanie ODM**: MongoDB object-document mapper
- **Redis Queue**: Task scheduling and processing
- **MongoDB**: Document database
- **Celery**: Distributed task queue

## Project Structure

```
journeyai/
├── app/
│   ├── api/                  # FastAPI routes
│   ├── core/                 # Core configurations
│   ├── db/                   # Database connections
│   ├── models/               # Beanie ODM models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   ├── external/             # External API integrations
│   ├── tasks/                # Redis queue tasks
│   └── utils/                # Utility functions
├── tests/                    # Test directory
├── .env.example              # Example environment variables
└── pyproject.toml            # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB
- Redis

### Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -e .
   ```
4. Copy `.env.example` to `.env` and configure environment variables
5. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

## Development

- **API documentation**: Available at `/docs` when the server is running
- **Tests**: Run with `pytest` 