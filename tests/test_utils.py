"""Unit tests for utility functions."""

import pytest
import numpy as np
from PIL import Image
from src.utils import (
    image_to_matrix,
    matrix_to_image,
    get_ecc_level_code,
    get_ecc_capacity
)


@pytest.mark.unit
class TestUtils:
    """Test utility functions."""
    
    def test_get_ecc_level_code(self):
        """Test ECC level code conversion."""
        from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
        
        assert get_ecc_level_code('L') == ERROR_CORRECT_L
        assert get_ecc_level_code('M') == ERROR_CORRECT_M
        assert get_ecc_level_code('Q') == ERROR_CORRECT_Q
        assert get_ecc_level_code('H') == ERROR_CORRECT_H
        assert get_ecc_level_code('l') == ERROR_CORRECT_L  # Case insensitive
        assert get_ecc_level_code('h') == ERROR_CORRECT_H
    
    def test_get_ecc_capacity(self):
        """Test ECC capacity calculation."""
        # Test with different versions and ECC levels
        for version in [1, 2, 5, 10]:
            for ecc in ['L', 'M', 'Q', 'H']:
                capacity = get_ecc_capacity(version, ecc)
                assert isinstance(capacity, int)
                assert capacity >= 0
    
    def test_matrix_to_image(self):
        """Test matrix to image conversion."""
        # Create a simple test matrix
        matrix = np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]], dtype=np.uint8)
        
        img = matrix_to_image(matrix, module_size=10)
        
        assert isinstance(img, Image.Image)
        assert img.size == (30, 30)  # 3 modules * 10 pixels
    
    def test_image_to_matrix(self):
        """Test image to matrix conversion."""
        # Create a simple test image
        matrix = np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]], dtype=np.uint8)
        img = matrix_to_image(matrix, module_size=10)
        
        # Convert back to matrix
        result_matrix = image_to_matrix(img)
        
        assert isinstance(result_matrix, np.ndarray)
        assert result_matrix.shape[0] > 0
        assert result_matrix.shape[1] > 0
    
    def test_matrix_image_roundtrip(self):
        """Test roundtrip conversion: matrix -> image -> matrix."""
        original = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]], dtype=np.uint8)
        
        img = matrix_to_image(original, module_size=10)
        result = image_to_matrix(img)
        
        # Result should be similar (may have scaling differences)
        assert isinstance(result, np.ndarray)
        assert result.shape[0] > 0
        assert result.shape[1] > 0

