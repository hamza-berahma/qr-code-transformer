.PHONY: help test test-unit test-integration test-e2e test-cov format lint clean install dev-install

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev-install   - Install with dev dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e      - Run E2E tests only"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make format        - Format code with black"
	@echo "  make lint          - Check code formatting"
	@echo "  make clean         - Clean build artifacts"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-cov black

test:
	pytest tests/ -v

test-unit:
	pytest tests/ -m "unit" -v

test-integration:
	pytest tests/integration/ -m "integration" -v

test-e2e:
	pytest tests/e2e/ -m "e2e" -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

format:
	black src/ web/ desktop/ tests/ --line-length 100

lint:
	black --check src/ web/ desktop/ tests/ --line-length 100

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -rf build/ dist/ htmlcov/ .coverage coverage.xml
