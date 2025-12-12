"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def sample_messages():
    """Sample message pairs for testing."""
    return [
        ('A', 'B'),
        ('Hello', 'World'),
        ('Test', 'Data'),
        ('123', '456'),
        ('', 'A'),  # Empty to something
    ]

@pytest.fixture
def transformer_m():
    """Transformer with Medium ECC level."""
    from src.transformer import QRTransformer
    return QRTransformer(ecc_level='M')

@pytest.fixture
def transformer_h():
    """Transformer with High ECC level."""
    from src.transformer import QRTransformer
    return QRTransformer(ecc_level='H')

@pytest.fixture
def encoder():
    """QR encoder for testing."""
    from src.qr_encoder import QREncoder
    return QREncoder(ecc_level='M')
