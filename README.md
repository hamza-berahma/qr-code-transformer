# QR Code Transformation Tool

<div align="center">

![QR Code Transformation](web/static/favicon.png)

**Transform QR codes with minimal module changes using Reed-Solomon error correction**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-black.svg)](https://railway.app)

[Live Demo](#-live-demo) • [Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

## 🎯 Overview

Transform a QR code encoding message **A** into a QR code that decodes to message **B**, using minimal module changes by exploiting Reed-Solomon error correction's non-bijective nature.

This project implements **four advanced algorithms** (Naive, ILP, QArt, and Hybrid Control Model) to find the optimal transformation with the fewest module flips.

## ✨ Features

- **🔬 Four Algorithms**: Naive, ILP (Integer Linear Programming), QArt (RS Linearity), and Hybrid Control Model
- **🎯 Optimal Results**: Automatically tests all 4 ECC levels (L, M, Q, H) and selects the best combination
- **🌐 Modern Web Interface**: Beautiful, responsive SPA-like UI with real-time transformations
- **🖥️ Desktop GUI**: Tkinter-based desktop application
- **📊 Detailed Insights**: ECC capacity analysis, algorithm comparison, and transformation statistics
- **📈 Visualization**: Side-by-side comparison of original, target, transformed, and change highlights
- **⚡ Fast & Efficient**: Optimized algorithms with lazy loading and caching
- **🚀 Production Ready**: Deployed on Railway with health checks and auto-scaling

## 🚀 Live Demo

**Try it now**: [https://web-production-a66f0.up.railway.app/](https://web-production-a66f0.up.railway.app/)

The web interface provides:
- Real-time QR code transformation
- Algorithm comparison across all ECC levels
- Visual change highlighting
- Detailed performance metrics

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/hamza-berahma/qr-code-transformer.git
cd qr-code-transformer

# Install dependencies
pip install -r requirements.txt
```

## 💻 Usage

### Web Interface (Recommended)

```bash
# Start the web server
cd web
python -m uvicorn app:app --reload
```

Visit `http://localhost:8000` to access the web interface.

### Desktop GUI

```bash
python desktop/gui.py
```

### Python API

```python
from src.transformer import QRTransformer

# Initialize transformer
transformer = QRTransformer()

# Transform QR code
result = transformer.transform(
    message_a="Hello",
    message_b="World"
)

# Access results
print(f"Minimal changes: {result.min_flips}")
print(f"Modules to flip: {result.flip_positions}")
print(f"Within ECC capacity: {result.within_ecc}")
print(f"Best algorithm: {result.algorithm}")
```

## 🏗️ Project Structure

```
qr-code-transformer/
├── src/                    # Core transformation algorithms
│   ├── transformer.py      # Main transformer (orchestrates all algorithms)
│   ├── ilp_transformer.py  # ILP-based optimal solver
│   ├── qart_transformer.py # QArt algorithm (RS linearity)
│   ├── hybrid_transformer.py # Hybrid Control Model
│   ├── qr_encoder.py       # QR code encoding/decoding
│   ├── rs_analysis.py      # Reed-Solomon analysis
│   └── visualizer.py       # Visualization utilities
├── web/                    # FastAPI web application
│   ├── app.py              # FastAPI application
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, favicon
├── desktop/                # Desktop GUI application
├── tests/                  # Comprehensive test suite
│   ├── integration/        # Integration tests
│   └── e2e/               # End-to-end tests
├── examples/               # Example scripts
└── paper/                  # Research paper (LaTeX)
```

## 🔬 Algorithms

### 1. Naive Algorithm
Direct module flipping without ECC exploitation. Baseline for comparison.

### 2. ILP (Integer Linear Programming)
Optimal solution using OR-Tools/SCIP solver. Guarantees minimum flips within ECC capacity.

### 3. QArt Algorithm
Heuristic using Reed-Solomon linearity, padding bits, and coordinate descent. Fast and effective.

### 4. Hybrid Control Model ⭐
**Our novel approach**: Two-phase algorithm combining:
- **Phase 1**: Padding control (zero-error mathematical manipulation)
- **Phase 2**: Strategic error injection (RS error budget utilization)

## 📊 Performance

The transformer automatically:
- Tests all 4 ECC levels (L ~7%, M ~15%, Q ~25%, H ~30%)
- Runs all applicable algorithms (QArt, ILP, Hybrid)
- Selects the combination with minimum module flips
- Provides detailed comparison statistics

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test types
pytest tests/ -m unit        # Unit tests
pytest tests/ -m integration # Integration tests
pytest tests/ -m e2e         # End-to-end tests
```

## 🚢 Deployment

### Railway (Recommended)

The app is configured for Railway deployment:

```bash
# Railway auto-detects and deploys from GitHub
# Configuration files:
# - railway.json
# - railway.toml
# - Procfile
```

### Docker

```bash
docker build -t qr-transformer .
docker run -p 8000:8000 qr-transformer
```

### Other Platforms

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Render.com
- Heroku
- Local production

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running the web server
- **Research Paper**: See `paper/` directory for detailed algorithm descriptions
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🛠️ Development

```bash
# Format code
black src/ web/ desktop/ tests/

# Run linter
flake8 src/ web/ desktop/

# Run tests
pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **qrcode** library for QR code generation
- **ortools** for Integer Linear Programming optimization
- **FastAPI** for the modern web framework
- **Reed-Solomon** error correction research community

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.

## 🔗 Links

- **Live Demo**: [https://web-production-a66f0.up.railway.app/](https://web-production-a66f0.up.railway.app/)
- **GitHub Repository**: [https://github.com/hamza-berahma/qr-code-transformer](https://github.com/hamza-berahma/qr-code-transformer)
- **Issues**: [GitHub Issues](https://github.com/hamza-berahma/qr-code-transformer/issues)

---

<div align="center">

Made with ❤️ by [hamza-berahma](https://github.com/hamza-berahma)

⭐ Star this repo if you find it useful!

</div>
