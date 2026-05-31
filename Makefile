.PHONY: up down setup test clean help

# Variáveis
DOCKER_COMPOSE = docker compose
APP_SERVICE = app

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Sobe a infraestrutura e executa o setup completo (Comando Único)
	$(DOCKER_COMPOSE) up -d --build
	@echo "Aguardando containers ficarem saudáveis..."
	@sleep 10
	$(MAKE) setup
	@echo "🚀 Tudo pronto! Dashboard em http://localhost:8501"

down: ## Remove todos os containers e redes
	$(DOCKER_COMPOSE) down

setup: ## Executa apenas o script de ingestão e transformação
	$(DOCKER_COMPOSE) exec -t $(APP_SERVICE) ./setup.sh

test: ## Executa a suite de testes completa
	$(DOCKER_COMPOSE) exec -t $(APP_SERVICE) pytest tests/

clean: ## Limpa volumes e artefatos temporários
	$(DOCKER_COMPOSE) down -v
	rm -rf northwind_transformations/target northwind_transformations/logs
	find . -type d -name "__pycache__" -exec rm -rf {} +
