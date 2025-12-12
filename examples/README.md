# Examples

## Basic Usage

Run the basic transformation example:

```bash
python examples/basic_usage.py
```

This will:
1. Transform a QR code encoding "Hello" to decode as "World"
2. Show statistics about the transformation
3. Generate a visualization showing the changes
4. Save the result to `transformation_result.png`

## Using the Web Interface

Start the FastAPI server:

```bash
cd web
uvicorn app:app --reload
```

Then visit `http://localhost:8000` in your browser.

## Using the Desktop GUI

Run the Tkinter desktop application:

```bash
python desktop/gui.py
```

## Python API

```python
from src.transformer import QRTransformer

transformer = QRTransformer(ecc_level='M')
result = transformer.transform("Hello", "World")

print(f"Minimal flips: {result.min_flips}")
print(f"Flip positions: {result.flip_positions}")
```

