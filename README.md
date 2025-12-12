# QR Code Transformation Tool

Transform a QR code encoding message A into a QR code that decodes to message B, using minimal module changes by exploiting Reed-Solomon error correction's non-bijective nature.

## Problem Statement

Given a QR code that encodes message A, find the minimal set of module (bit) flips required to transform it into a QR code that decodes to message B. This exploits the fact that Reed-Solomon error correction is non-bijective: multiple bit patterns can decode to the same message.

## Features

- **Minimal Transformation**: Find the smallest number of module changes to transform QR(A) → QR(B)
- **ECC-Aware**: Respect error correction capacity or find absolute minimum
- **Dual Algorithms**: Both exact (optimal) and heuristic (fast) approaches
- **Visualization**: See exactly which modules need to be flipped
- **Web & Desktop**: FastAPI web interface and Tkinter desktop GUI
- **Educational**: Insights into ECC capacity, RS block structure, and transformation analysis

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Web Interface

```bash
cd web
uvicorn app:app --reload
```

Visit `http://localhost:8000` to use the web interface.

### Desktop GUI

```bash
python desktop/gui.py
```

### Python API

```python
from src.transformer import QRTransformer

transformer = QRTransformer()
result = transformer.transform(message_a="Hello", message_b="World")
print(f"Minimal changes: {result.min_flips}")
print(f"Modules to flip: {result.flip_positions}")
```

## Project Structure

```
qr/
├── src/              # Core transformation logic
├── web/              # FastAPI web interface
├── desktop/          # Tkinter desktop GUI
├── tests/            # Test suite
└── examples/         # Example QR codes
```

## Algorithm

The transformation algorithm works by:

1. Encoding both messages A and B into QR codes
2. Extracting module matrices and codewords
3. Analyzing Reed-Solomon error correction structure
4. Finding alternative valid bit patterns that decode to B
5. Computing minimal flip set using exact/heuristic search

## Testing

The project includes comprehensive test coverage:

### Test Structure
- **Unit Tests** (`tests/`): Test individual components in isolation
- **Integration Tests** (`tests/integration/`): Test API endpoints and component interactions
- **E2E Tests** (`tests/e2e/`): Test complete workflows end-to-end

### Running Tests

```bash
# Run all tests
make test-all
# or
pytest tests/ -v

# Run only unit tests
make test-unit
# or
pytest tests/ -m "unit" -v

# Run only integration tests
make test-integration
# or
pytest tests/integration/ -m "integration" -v

# Run only E2E tests
make test-e2e
# or
pytest tests/e2e/ -m "e2e" -v

# Run with coverage
make test-cov
# or
pytest tests/ --cov=src --cov-report=html
```

### Test Markers

Tests are marked with:
- `@pytest.mark.unit` - Unit tests (fast)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests

### CI/CD

Tests run automatically on GitHub Actions for:
- Python 3.8, 3.9, 3.10, 3.11
- Unit, integration, and E2E test suites
- Code coverage reporting

## Development

### Code Formatting

```bash
# Format code
make format
# or
black src/ web/ desktop/ tests/

# Check formatting
make lint
```

### Project Structure

```
qr/
├── src/              # Core transformation logic
├── web/              # FastAPI web interface
├── desktop/          # Tkinter desktop GUI
├── tests/             # Test suite
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── e2e/          # End-to-end tests
└── examples/         # Example scripts
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Acknowledgments

- Uses `qrcode` library for QR code generation
- Uses `ortools` for Integer Linear Programming optimization
- Inspired by research on QR code error correction exploitation

