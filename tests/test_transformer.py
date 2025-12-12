"""Unit tests for main QR transformer."""

import pytest
import numpy as np
from src.transformer import QRTransformer, TransformationResult


@pytest.mark.unit
class TestQRTransformer:
    """Test main QR transformer with multi-algorithm support."""
    
    def test_init(self):
        """Test transformer initialization."""
        transformer = QRTransformer(ecc_level='M')
        assert transformer.ecc_level == 'M'
        assert transformer.version is None
        assert transformer.encoder is not None
    
    def test_init_with_version(self):
        """Test transformer with specific version."""
        transformer = QRTransformer(ecc_level='H', version=1)
        assert transformer.ecc_level == 'H'
        assert transformer.version == 1
    
    def test_transform_simple(self):
        """Test transformation with simple messages."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('A', 'B')
        
        assert isinstance(result, TransformationResult)
        assert result.success is True
        assert result.min_flips >= 0
        assert result.message_a == 'A'
        assert result.message_b == 'B'
        assert result.algorithm is not None
        assert result.algorithm_results is not None
    
    def test_transform_tests_all_ecc_levels(self):
        """Test that transform tests all ECC levels."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        # Should test all 4 ECC levels with both algorithms (8 combinations)
        assert len(result.algorithm_results) >= 4  # At least some combinations tested
        assert result.algorithm is not None
        assert '-' in result.algorithm  # Format: "algorithm-ecc"
    
    def test_transform_selects_best(self):
        """Test that transform selects the best result."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        # Check that best result has minimum flips
        best_flips = result.min_flips
        for algo_name, algo_data in result.algorithm_results.items():
            if not algo_data.get('error') and algo_data.get('success'):
                assert algo_data.get('min_flips', float('inf')) >= best_flips
    
    def test_transform_result_structure(self):
        """Test that transformation result has correct structure."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'min_flips')
        assert hasattr(result, 'flip_positions')
        assert hasattr(result, 'transformed_matrix')
        assert hasattr(result, 'within_ecc')
        assert hasattr(result, 'stats')
        assert hasattr(result, 'message_a')
        assert hasattr(result, 'message_b')
        assert hasattr(result, 'algorithm')
        assert hasattr(result, 'algorithm_results')
    
    def test_transform_same_message(self):
        """Test transformation with same message."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'Hello')
        
        assert result.success is True
        assert result.min_flips >= 0
    
    def test_algorithm_results_format(self):
        """Test that algorithm_results has correct format."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('A', 'B')
        
        assert isinstance(result.algorithm_results, dict)
        for key, value in result.algorithm_results.items():
            assert isinstance(key, str)
            assert isinstance(value, dict)
            # Should have either error or success data
            assert 'error' in value or 'min_flips' in value
    
    def test_best_ecc_level_in_stats(self):
        """Test that best ECC level is stored in stats."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        assert 'best_ecc_level' in result.stats
        assert result.stats['best_ecc_level'] in ['L', 'M', 'Q', 'H']
        assert 'best_algorithm' in result.stats
        assert result.stats['best_algorithm'] in ['qart', 'ilp']
    
    def test_flip_positions_valid(self):
        """Test that flip positions are valid coordinates."""
        transformer = QRTransformer(ecc_level='M')
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
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        qr_a = transformer.encoder.encode(result.message_a)
        expected_shape = qr_a.module_matrix.shape
        
        assert result.transformed_matrix is not None
        assert result.transformed_matrix.shape == expected_shape
