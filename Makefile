.DEFAULT_GOAL := help

SHELL=/bin/bash
VENV = .venv

# Detect the operating system and set the virtualenv bin directory
ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

setup: $(VENV)/bin/activate ## Set up the virtual environment

$(VENV)/bin/activate: setup.py requirements
	# Create new virtual environment if setup.py has changed
	python3 -m venv $(VENV)
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements/requirements-dev.txt
	$(VENV_BIN)/pip install -r requirements/requirements-client.txt
	$(VENV_BIN)/pip install -r requirements/requirements.txt
	$(VENV_BIN)/pip install -r requirements/requirements-tests.txt
	$(VENV_BIN)/pip install -r requirements/requirements-markdown-tests.txt
	touch $(VENV)/.venv-timestamp

testenv: $(VENV)/.testenv ## Set up the test environment

$(VENV)/.testenv: $(VENV)/bin/activate
	$(VENV_BIN)/pip install -e ".[openai]"
	$(VENV_BIN)/pip install -r requirements/requirements-dev.txt
	touch $(VENV)/.testenv

test: $(VENV)/.testenv ## Run unit tests
	$(VENV_BIN)/pytest src

.PHONY: test-doc
test-doc: $(VENV)/.testenv ## Run doctests
	$(VENV_BIN)/pytest --doctest-modules -k "not test_" src/core

.PHONY: coverage
coverage: setup ## Run tests and report coverage
	$(VENV_BIN)/pytest src --cov=src

# Configuration
PYTHON_VERSION ?= 3.10
DATABASE ?= postgres:14
DOCKER_TAG ?= synopkg/syntask-dev:latest
BENCHMARK_DIR := ./.benchmarks
CACHE_DIR := ~/.cache/uv
SYNTASK_API_URL := http://127.0.0.1:4200/api
WINDOWS_PYTHON_VERSIONS := 3.9 3.10 3.11 3.12

export PY_COLORS=1
export SYNTASK_EXPERIMENTAL_ENABLE_PYDANTIC_V2_INTERNALS=1

.PHONY: install
install: $(VENV)/.testenv ## Install project dependencies
	pip install -U uv
	uv pip install --upgrade --system -e .[dev]

.PHONY: docker-setup
docker-setup: $(VENV)/.testenv ## Build Docker image
	docker buildx build --build-arg PYTHON_VERSION=$(PYTHON_VERSION) --build-arg SYNTASK_EXTRAS=[dev] -t $(DOCKER_TAG) .

.PHONY: db-setup
db-setup: $(VENV)/.testenv ## Start PostgreSQL container
	docker run --name postgres --detach --health-cmd pg_isready --health-interval 10s --health-timeout 5s \
		--health-retries 5 --publish 5432:5432 --env POSTGRES_USER="syntask" --env POSTGRES_PASSWORD="syntask" \
		--env POSTGRES_DB="syntask" $(DATABASE)

.PHONY: redis-setup
redis-setup: $(VENV)/.testenv ## Start Redis container
	docker run --name redis --detach --publish 6379:6379 redis:latest

.PHONY: format
format: $(VENV)/bin/activate ## Format the code
	$(VENV_BIN)/pip install -r requirements/requirements-tests.txt
	pip install ruff
	bash scripts/format.sh

.PHONY: lint
lint: $(VENV)/bin/activate ## Lint the code
	bash scripts/lint.sh

.PHONY: run-tests
run-tests: ## Run unit tests
	pytest tests --numprocesses auto --maxprocesses 6 --dist worksteal --durations 26 --no-cov

.PHONY: docker-tests
docker-tests: docker-setup db-setup redis-setup ## Run Docker tests
	docker load --input /tmp/image.tar
	docker run --rm $(DOCKER_TAG) syntask version

.PHONY: start-server
start-server: ## Start the Syntask server
	SYNTASK_HOME=$(shell pwd) syntask server start & disown \
	SYNTASK_API_URL=$(SYNTASK_API_URL) ./scripts/wait-for-server.py

.PHONY: run-benchmarks
run-benchmarks: start-server ## Run benchmarks
	@HEAD_REF=$(shell git rev-parse --abbrev-ref HEAD)
	@GITHUB_SHA=$(shell git rev-parse HEAD)
	@if [ -z "$$HEAD_REF" ]; then \
		uniquename="main-$$GITHUB_SHA"; \
	else \
		uniquename="$$HEAD_REF"; \
	fi
	sanitized_uniquename=$${uniquename//[^a-zA-Z0-9_\-]/_}
	SYNTASK_API_URL=$(SYNTASK_API_URL) \
	python -m benches --ignore=benches/bench_import.py \
	--timeout=180 --benchmark-save="$${sanitized_uniquename}"

.PHONY: setup-docker
setup-docker: ## Set up Docker Buildx
	docker buildx create --use --driver-opt image=moby/buildkit:v0.12.5

.PHONY: trigger-docker-publish
trigger-docker-publish: ## Trigger Docker image publishing workflow
	gh workflow run publish-docker-images.yml -f publish_3_latest=true

.PHONY: cache
cache: ## Cache dependencies and benchmark results
	mkdir -p $(CACHE_DIR) $(BENCHMARK_DIR)

.PHONY: clean
clean: ## Clean up containers and cache
	-docker stop postgres redis
	-docker rm postgres redis
	rm -rf $(BENCHMARK_DIR) $(CACHE_DIR)

.PHONY: windows-tests
windows-tests: ## Run tests on Windows with SQLite
	@for PY_VER in $(WINDOWS_PYTHON_VERSIONS); do \
		echo "Setting up Python $$PY_VER on Windows"; \
		python -m pip install --upgrade pip; \
		pip install --upgrade --upgrade-strategy eager -e .[dev]; \
		echo "Running tests with Python $$PY_VER"; \
		pytest tests -vv --numprocesses auto --dist worksteal --exclude-services --durations=25; \
		pip uninstall -y -r requirements.txt; \
	done

.PHONY: docs
docs: ## Serve documentation
	@if [ ! -x "./scripts/serve_docs" ]; then \
		echo "Error: The 'serve_docs' script is not executable."; \
		echo "Please make it executable by running:"; \
		echo "  chmod +x \"./scripts/serve_docs\""; \
		echo "Then, run 'make docs' again."; \
		exit 1; \
	fi
	@./scripts/serve_docs

.PHONY: help
help:  ## Display this help screen
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' | sort
