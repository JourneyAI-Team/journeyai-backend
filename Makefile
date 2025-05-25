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

	docker compose down
	docker compose up -d
	honcho -e .env.local start
	
	@printf "$(GREEN)Local development environment started.$(NC)\n"
