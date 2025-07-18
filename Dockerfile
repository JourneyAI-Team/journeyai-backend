# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        nodejs \
        npm \
        parallel \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Set work directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Configure poetry: Don't create virtual env, install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Install the application
RUN poetry install --no-dev

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser -m \
    && chown -R appuser:appuser /app

# Configure npm directories for the appuser (as root)
RUN mkdir -p /home/appuser/.npm /home/appuser/.npm-global \
    && chown -R appuser:appuser /home/appuser/.npm /home/appuser/.npm-global

# Switch to appuser
USER appuser

# Set npm config for the user (using user-level config)
RUN npm config set cache /home/appuser/.npm && \
    npm config set prefix /home/appuser/.npm-global

# Pre-install the MCP package as the user (so it goes to the right location)
RUN npm install -g search1api-mcp

# Add npm global bin to PATH
ENV PATH="/home/appuser/.npm-global/bin:$PATH"

# Expose port 8000
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "app.main"] 