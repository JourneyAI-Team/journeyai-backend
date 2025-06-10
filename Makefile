RED=\033[0;31m
GREEN=\033[0;32m
BLUE=\033[0;34m
BOLD=\033[1m
UNDERLINE=\033[4m
NC=\033[0m # No Color

setup-local:
	@printf "$(BLUE)Setting up local development environment...$(NC)\n"

	@if [ ! -f .env.local ]; then \
		printf "$(GREEN)Creating .env.local from .env.example...$(NC)\n"; \
		cp .env.example .env.local; \
	fi

	poetry install
	poetry shell

	@printf "$(GREEN)Local setup complete.$(NC)\n"
	@printf "$(RED)Please add your external API keys to the .env.local file.$(NC)\n"


run-local:
	@printf "$(BLUE)Starting local development environment...$(NC)\n"

	# Kill any processes connected to Redis
	@pids=$$(sudo lsof -i :6379 | grep ESTABLISHED | awk '{print $$2}' | sort -u); \
	if [ -n "$$pids" ]; then \
		echo "Killing Redis-connected processes: $$pids"; \
		sudo kill -9 $$pids; \
	else \
		echo "No Redis-connected processes to kill."; \
	fi

	docker compose -f docker-compose.local.yaml down
	docker compose -f docker-compose.local.yaml up -d
	honcho -e .env.local start

	@printf "$(GREEN)Local development environment started.$(NC)\n"

run-production:
	@printf "$(BLUE)Starting production environment...$(NC)\n"

	@if [ ! -f .env.prod ]; then \
		printf "$(RED)Error: .env.prod file not found!$(NC)\n"; \
		printf "$(RED)Please create .env.prod with your production environment variables.$(NC)\n"; \
		printf "$(RED)Required variables:$(NC)\n"; \
		printf "$(RED)  - ENVIRONMENT=production$(NC)\n"; \
		printf "$(RED)  - SECRET_KEY=your-secret-key$(NC)\n"; \
		printf "$(RED)  - MONGODB_URL=mongodb://mongodb:27017$(NC)\n"; \
		printf "$(RED)  - QDRANT_URL=http://qdrant:6333$(NC)\n"; \
		printf "$(RED)  - REDIS_HOST=redis$(NC)\n"; \
		printf "$(RED)  - OPENAI_API_KEY=your-api-key$(NC)\n"; \
		printf "$(RED)  - GROQ_API_KEY=your-api-key$(NC)\n"; \
		exit 1; \
	fi

	docker compose down
	docker compose build
	docker compose up -d

	@printf "$(GREEN)Production environment started.$(NC)\n"

stop-local:
	@printf "$(BLUE)Stopping local development environment...$(NC)\n"
	docker compose -f docker-compose.local.yaml down
	@printf "$(GREEN)Local environment stopped.$(NC)\n"

stop-production:
	@printf "$(BLUE)Stopping production environment...$(NC)\n"
	docker compose down
	@printf "$(GREEN)Production environment stopped.$(NC)\n"
