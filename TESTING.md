# Testing Guide

## Overview

This project uses pytest for testing with comprehensive coverage including unit, integration, and end-to-end tests.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_transformer.py      # Unit tests for transformer
├── test_rs_analysis.py      # Unit tests for RS analysis
├── test_qr_encoder.py       # Unit tests for QR encoder
├── test_visualizer.py        # Unit tests for visualizer
├── test_insights.py          # Unit tests for insights
├── integration/
│   └── test_api.py          # Integration tests for API
└── e2e/
    └── test_e2e.py          # End-to-end tests
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### By Category
```bash
# Unit tests only
pytest tests/ -m "unit" -v

# Integration tests only
pytest tests/integration/ -m "integration" -v

# E2E tests only
pytest tests/e2e/ -m "e2e" -v
```

### With Coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

This generates:
- Terminal coverage report
- HTML report in `htmlcov/index.html`

### Skip Slow Tests
```bash
pytest tests/ -v -m "not slow"
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

## Writing Tests

### Unit Test Example
```python
import pytest
from src.transformer import QRTransformer

@pytest.mark.unit
def test_basic_transformation():
    transformer = QRTransformer(ecc_level='M')
    result = transformer.transform("Hello", "World")
    assert result.success
    assert result.min_flips > 0
```

### Integration Test Example
```python
import pytest
from fastapi.testclient import TestClient
from web.app import app

@pytest.mark.integration
def test_api_endpoint():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
```

### E2E Test Example
```python
import pytest

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_workflow():
    # Test complete transformation workflow
    transformer = QRTransformer()
    result = transformer.transform("A", "B")
    # ... full workflow test
```

## Fixtures

Shared fixtures are defined in `tests/conftest.py`:

- `transformer` - QRTransformer instance
- `encoder` - QREncoder instance
- `rs_analyzer` - RSAnalyzer instance
- `sample_messages` - Sample test messages
- `client` - FastAPI test client (integration tests)

## Continuous Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

See `.github/workflows/test.yml` for CI configuration.

## Best Practices

1. **Isolation**: Each test should be independent
2. **Naming**: Use descriptive test names
3. **Fixtures**: Use fixtures for common setup
4. **Markers**: Mark tests appropriately (unit/integration/e2e)
5. **Assertions**: Use specific assertions with helpful messages
6. **Coverage**: Aim for >80% code coverage

## Debugging Tests

### Run with verbose output
```bash
pytest tests/ -vv
```

### Run specific test
```bash
pytest tests/test_transformer.py::test_basic_transformation -v
```

### Run with print statements
```bash
pytest tests/ -v -s
```

### Run with pdb debugger
```bash
pytest tests/ --pdb
```

