"""Comprehensive integration tests."""

import pytest
import numpy as np
from src.transformer import QRTransformer
from src.visualizer import QRVisualizer
from src.insights import generate_insights


@pytest.mark.integration
class TestComprehensiveIntegration:
    """Comprehensive integration tests."""
    
    def test_full_workflow(self):
        """Test complete transformation workflow."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        # Verify result
        assert result.success
        assert result.min_flips >= 0
        
        # Test visualization
        visualizer = QRVisualizer()
        qr_a = transformer.encoder.encode(result.message_a)
        qr_b = transformer.encoder.encode(result.message_b)
        
        img = visualizer.create_comparison_grid(
            qr_a.module_matrix,
            qr_b.module_matrix,
            result.transformed_matrix,
            result.flip_positions
        )
        
        assert img is not None
        assert img.size[0] > 0
        assert img.size[1] > 0
    
    def test_insights_generation(self):
        """Test insights generation."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Hello', 'World')
        
        qr_a = transformer.encoder.encode(result.message_a)
        qr_b = transformer.encoder.encode(result.message_b)
        
        insights = generate_insights(result, transformer.encoder, qr_a.module_matrix, qr_b.module_matrix)
        
        assert 'transformation_summary' in insights
        assert 'ecc_info' in insights
        assert 'matrix_info' in insights
        assert 'messages' in insights
    
    def test_all_ecc_levels_work(self):
        """Test that all ECC levels produce valid results."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('Test', 'Data')
        
        # Should test all ECC levels automatically
        assert len(result.algorithm_results) >= 4
        
        # All successful results should have valid data
        for algo_name, algo_data in result.algorithm_results.items():
            if not algo_data.get('error') and algo_data.get('success'):
                assert 'min_flips' in algo_data
                assert 'ecc_level' in algo_data
                assert algo_data['ecc_level'] in ['L', 'M', 'Q', 'H']
    
    def test_algorithm_comparison(self):
        """Test that algorithm comparison works correctly."""
        transformer = QRTransformer(ecc_level='M')
        result = transformer.transform('A', 'B')
        
        # Should have results from multiple algorithms
        assert len(result.algorithm_results) > 0
        
        # Best result should have minimum flips
        best_flips = result.min_flips
        for algo_name, algo_data in result.algorithm_results.items():
            if not algo_data.get('error') and algo_data.get('success'):
                assert algo_data.get('min_flips', float('inf')) >= best_flips

