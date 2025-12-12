"""Unit tests for QArt transformer."""

import pytest
import numpy as np
from src.qart_transformer import QArtTransformer, QArtResult


@pytest.mark.unit
class TestQArtTransformer:
    """Test QArt-based QR code transformation."""
    
    def test_init(self):
        """Test QArt transformer initialization."""
        transformer = QArtTransformer(ecc_level='H')
        assert transformer.ecc_level == 'H'
        assert transformer.version is None
    
    def test_init_with_version(self):
        """Test QArt transformer with specific version."""
        transformer = QArtTransformer(ecc_level='M', version=1)
        assert transformer.ecc_level == 'M'
        assert transformer.version == 1
    
    def test_transform_simple(self):
        """Test transformation with simple messages."""
        transformer = QArtTransformer(ecc_level='H')
        result = transformer.transform('A', 'B')
        
        assert isinstance(result, QArtResult)
        assert result.success is True
        assert result.min_flips >= 0
        assert len(result.flip_positions) == result.min_flips
        assert result.message_a == 'A'
        assert result.message_b == 'B'
        assert result.transformed_matrix is not None
    
    def test_transform_same_message(self):
        """Test transformation with same message."""
        transformer = QArtTransformer(ecc_level='H')
        result = transformer.transform('Hello', 'Hello')
        
        assert result.success is True
        assert result.min_flips >= 0
    
    def test_transform_different_ecc_levels(self):
        """Test transformation with different ECC levels."""
        for ecc in ['L', 'M', 'Q', 'H']:
            transformer = QArtTransformer(ecc_level=ecc)
            result = transformer.transform('Test', 'Data')
            assert result.success is True
            assert result.min_flips >= 0
    
    def test_basis_vectors_extraction(self):
        """Test that basis vectors are extracted."""
        transformer = QArtTransformer(ecc_level='H')
        result = transformer.transform('Hello', 'World')
        
        assert hasattr(result, 'basis_vectors')
        # Basis vectors should be a dict or None
        assert result.basis_vectors is None or isinstance(result.basis_vectors, dict)
    
    def test_result_structure(self):
        """Test that result has correct structure."""
        transformer = QArtTransformer(ecc_level='H')
        result = transformer.transform('Hello', 'World')
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'min_flips')
        assert hasattr(result, 'flip_positions')
        assert hasattr(result, 'transformed_matrix')
        assert hasattr(result, 'within_ecc')
        assert hasattr(result, 'stats')
        assert hasattr(result, 'message_a')
        assert hasattr(result, 'message_b')
    
    def test_flip_positions_valid(self):
        """Test that flip positions are valid coordinates."""
        transformer = QArtTransformer(ecc_level='H')
        result = transformer.transform('A', 'B')
        
        if result.flip_positions:
            import qrcode
            qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=1, border=0)
            qr.add_data('A')
            qr.make(fit=True)
            matrix = np.array(qr.get_matrix(), dtype=int)
            height, width = matrix.shape
            
            for row, col in result.flip_positions:
                assert isinstance(row, (int, np.integer))
                assert isinstance(col, (int, np.integer))
                assert 0 <= row < height
                assert 0 <= col < width

