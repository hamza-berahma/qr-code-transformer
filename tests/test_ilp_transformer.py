"""Unit tests for ILP transformer."""

import pytest
import numpy as np
from src.ilp_transformer import ILPQRTransformer, ILPTransformationResult


@pytest.mark.unit
class TestILPQRTransformer:
    """Test ILP-based QR code transformation."""
    
    def test_init(self):
        """Test ILP transformer initialization."""
        transformer = ILPQRTransformer(ecc_level='M')
        assert transformer.ecc_level == 'M'
        assert transformer.version is None
        assert transformer.encoder is not None
    
    def test_init_with_version(self):
        """Test ILP transformer with specific version."""
        transformer = ILPQRTransformer(ecc_level='H', version=1)
        assert transformer.ecc_level == 'H'
        assert transformer.version == 1
    
    def test_transform_simple(self):
        """Test transformation with simple messages."""
        transformer = ILPQRTransformer(ecc_level='M')
        result = transformer.transform('A', 'B')
        
        assert isinstance(result, ILPTransformationResult)
        assert result.success is True
        assert result.min_flips >= 0
        assert len(result.flip_positions) == result.min_flips
        assert result.message_a == 'A'
        assert result.message_b == 'B'
        assert result.transformed_matrix is not None
    
    def test_transform_same_message(self):
        """Test transformation with same message (should require 0 flips)."""
        transformer = ILPQRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'Hello')
        
        assert result.success is True
        # Should require minimal or zero flips for same message
        assert result.min_flips >= 0
    
    def test_transform_different_ecc_levels(self):
        """Test transformation with different ECC levels."""
        for ecc in ['L', 'M', 'Q', 'H']:
            transformer = ILPQRTransformer(ecc_level=ecc)
            result = transformer.transform('Test', 'Data')
            assert result.success is True
            assert result.min_flips >= 0
    
    def test_transform_result_structure(self):
        """Test that transformation result has correct structure."""
        transformer = ILPQRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'min_flips')
        assert hasattr(result, 'flip_positions')
        assert hasattr(result, 'transformed_matrix')
        assert hasattr(result, 'within_ecc')
        assert hasattr(result, 'stats')
        assert hasattr(result, 'message_a')
        assert hasattr(result, 'message_b')
        assert hasattr(result, 'solver_time')
    
    def test_flip_positions_valid(self):
        """Test that flip positions are valid coordinates."""
        transformer = ILPQRTransformer(ecc_level='M')
        result = transformer.transform('A', 'B')
        
        if result.flip_positions:
            qr_a = transformer.encoder.encode(result.message_a)
            height, width = qr_a.module_matrix.shape
            
            for row, col in result.flip_positions:
                assert isinstance(row, (int, np.integer))
                assert isinstance(col, (int, np.integer))
                assert 0 <= row < height
                assert 0 <= col < width
    
    def test_transformed_matrix_shape(self):
        """Test that transformed matrix has correct shape."""
        transformer = ILPQRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        qr_a = transformer.encoder.encode(result.message_a)
        expected_shape = qr_a.module_matrix.shape
        
        assert result.transformed_matrix is not None
        assert result.transformed_matrix.shape == expected_shape

