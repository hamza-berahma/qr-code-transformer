# Quick Start Guide

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface (Recommended)

1. Start the server:
```bash
cd web
uvicorn app:app --reload
```

2. Open your browser to `http://localhost:8000`

3. Choose input type:
   - **Two Messages**: Enter message A and message B
   - **QR Image + Target Message**: Upload a QR code image and enter target message

4. Configure options:
   - ECC Level: Choose error correction level (L/M/Q/H)
   - Use Exact Algorithm: For optimal results (slower)
   - Respect ECC Capacity: Only find solutions within error correction limits

5. Click "Transform" to see results

### Desktop GUI

```bash
python desktop/gui.py
```

### Command Line / Python API

```python
from src.transformer import QRTransformer

transformer = QRTransformer(ecc_level='M')
result = transformer.transform("Hello", "World")

print(f"Minimal flips: {result.min_flips}")
print(f"Within ECC: {result.within_ecc}")
```

### Example Script

```bash
python examples/basic_usage.py
```

## How It Works

1. **Encode both messages**: Creates QR codes for message A and message B
2. **Extract module matrices**: Gets the binary module patterns
3. **Analyze differences**: Computes which modules need to flip
4. **Exploit RS non-bijectivity**: Finds minimal changes by leveraging error correction
5. **Visualize results**: Shows side-by-side comparison with highlighted changes

## Key Features

- **Minimal Transformation**: Finds the smallest number of module flips
- **ECC-Aware**: Respects or exploits error correction capacity
- **Dual Algorithms**: Exact (optimal) and heuristic (fast) approaches
- **Visualization**: See exactly which modules need to change
- **Web & Desktop**: Choose your preferred interface
- **Educational**: Insights into ECC capacity and transformation analysis

## Troubleshooting

- **Import errors**: Make sure you're in the project root directory
- **Image not loading**: Check that the QR code image is valid and readable
- **Transformation fails**: Try a different ECC level or shorter messages
- **Web server won't start**: Check that port 8000 is available

