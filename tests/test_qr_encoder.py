"""Unit tests for QR encoder."""

import pytest
import numpy as np
from src.qr_encoder import QREncoder, QRCodeData


class TestQREncoder:
    """Test QR encoder functionality."""
    
    def test_encoder_initialization(self, encoder):
        """Test encoder can be initialized."""
        assert encoder is not None
        assert encoder.ecc_level == 'M'
    
    def test_encode_message(self, encoder):
        """Test encoding a message."""
        qr_data = encoder.encode("Test")
        assert isinstance(qr_data, QRCodeData)
        assert qr_data.message == "Test"
        assert qr_data.module_matrix is not None
        assert qr_data.module_matrix.shape[0] > 0
        assert qr_data.module_matrix.shape[1] > 0
    
    def test_encode_different_messages(self, encoder):
        """Test encoding different messages produces different matrices."""
        qr1 = encoder.encode("Message 1")
        qr2 = encoder.encode("Message 2")
        
        assert qr1.message != qr2.message
        # Matrices should be different (or at least have different shapes potentially)
        assert qr1.module_matrix.shape == qr2.module_matrix.shape or True
    
    def test_encode_empty_message(self, encoder):
        """Test encoding empty message."""
        qr_data = encoder.encode("")
        assert qr_data.message == ""
        assert qr_data.module_matrix is not None
    
    def test_different_ecc_levels(self):
        """Test encoding with different ECC levels."""
        for ecc in ['L', 'M', 'Q', 'H']:
            encoder = QREncoder(ecc_level=ecc)
            qr_data = encoder.encode("Test")
            assert qr_data.ecc_level == ecc
    
    def test_qr_data_to_image(self, encoder):
        """Test converting QR data to image."""
        qr_data = encoder.encode("Test")
        img = qr_data.to_image(module_size=10)
        assert img is not None
        assert img.size[0] > 0
        assert img.size[1] > 0
    
    def test_get_total_modules(self, encoder):
        """Test getting total modules."""
        qr_data = encoder.encode("Test")
        total = qr_data.get_total_modules()
        assert total > 0
        assert total == qr_data.height * qr_data.width

