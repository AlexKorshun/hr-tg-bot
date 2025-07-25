# config
GOOSE_VER := v3.24.1
BIN_DIR := $(CURDIR)/bin
ENV_LOCAL_FILE  := ./.env.local

# toolse
GOOSE := $(BIN_DIR)/goose
COMPOSE := docker-compose

.PHONY: compose-up
compose-up:
	$(COMPOSE) up -d

.PHONY: compose-build
compose-build:
	$(COMPOSE) up --build -d

.PHONY: compose-start
compose-start:
	$(COMPOSE) start

.PHONY: compose-stop
compose-stop:
	$(COMPOSE) stop


$(GOOSE):
	GOBIN=$(BIN_DIR) go install github.com/pressly/goose/v3/cmd/goose@$(GOOSE_VER)


.PHONY: migrate-up
migrate-up: $(GOOSE)
	if [ -f $(ENV_LOCAL_FILE) ]; then \
		set -a; . $(ENV_LOCAL_FILE); set +a; \
	fi; \
	$(GOOSE) -dir ./migrations postgres "$$WRITE_DSN" up

.PHONY: migrate-down
migrate-down: $(GOOSE)
	if [ -f $(ENV_LOCAL_FILE) ]; then \
		set -a; . $(ENV_LOCAL_FILE); set +a; \
	fi; \
	$(GOOSE) -dir ./migrations postgres "$$WRITE_DSN" down

.PHONY: requirements
requirements:
	pip freeze -> requirements.txt

.PHONY: install-requirements
install-requirements:
	pip install -r requirements.txt