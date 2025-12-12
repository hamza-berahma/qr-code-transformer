"""End-to-end tests for the complete transformation workflow."""

import pytest
import numpy as np
from src.transformer import QRTransformer
from src.visualizer import QRVisualizer
from src.insights import generate_insights


@pytest.mark.e2e
class TestE2ETransformation:
    """End-to-end tests for complete transformation workflow."""
    
    @pytest.fixture
    def transformer(self):
        """Create transformer for E2E tests."""
        return QRTransformer(ecc_level='M')
    
    @pytest.fixture
    def visualizer(self):
        """Create visualizer for E2E tests."""
        return QRVisualizer(module_size=10)
    
    @pytest.mark.slow
    def test_complete_transformation_workflow(self, transformer, visualizer):
        """Test complete transformation workflow from start to finish."""
        # Step 1: Transform messages
        result = transformer.transform(
            message_a="Hello",
            message_b="World",
            use_exact=True,
            respect_ecc=False
        )
        
        assert result.success
        assert result.min_flips >= 0
        assert len(result.flip_positions) == result.min_flips
        
        # Step 2: Get matrices
        qr_a = transformer.encoder.encode(result.message_a)
        qr_b = transformer.encoder.encode(result.message_b)
        
        matrix_a = qr_a.module_matrix
        matrix_b = qr_b.module_matrix
        
        # Step 3: Ensure dimensions match
        if matrix_a.shape != matrix_b.shape:
            min_h = min(matrix_a.shape[0], matrix_b.shape[0])
            min_w = min(matrix_a.shape[1], matrix_b.shape[1])
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
            if result.transformed_matrix is not None:
                result.transformed_matrix = result.transformed_matrix[:min_h, :min_w]
        
        # Step 4: Generate visualization
        comparison = visualizer.create_comparison_grid(
            matrix_a, matrix_b, result.transformed_matrix, result.flip_positions
        )
        
        assert comparison is not None
        assert comparison.size[0] > 0
        assert comparison.size[1] > 0
        
        # Step 5: Generate insights
        insights = generate_insights(result, transformer.encoder, matrix_a, matrix_b)
        
        assert insights is not None
        assert 'transformation_summary' in insights
        assert insights['transformation_summary']['min_flips'] == result.min_flips
    
    @pytest.mark.slow
    def test_different_ecc_levels_e2e(self, visualizer):
        """Test E2E workflow with different ECC levels."""
        for ecc in ['L', 'M', 'Q', 'H']:
            transformer = QRTransformer(ecc_level=ecc)
            result = transformer.transform("A", "B", use_exact=True, respect_ecc=False)
            
            assert result.success
            assert result.min_flips >= 0
            
            qr_a = transformer.encoder.encode(result.message_a)
            qr_b = transformer.encoder.encode(result.message_b)
            
            matrix_a = qr_a.module_matrix
            matrix_b = qr_b.module_matrix
            
            if matrix_a.shape != matrix_b.shape:
                min_h = min(matrix_a.shape[0], matrix_b.shape[0])
                min_w = min(matrix_a.shape[1], matrix_b.shape[1])
                matrix_a = matrix_a[:min_h, :min_w]
                matrix_b = matrix_b[:min_h, :min_w]
            
            comparison = visualizer.create_comparison_grid(
                matrix_a, matrix_b, result.transformed_matrix, result.flip_positions
            )
            
            assert comparison is not None
    
    @pytest.mark.slow
    def test_exact_vs_heuristic_e2e(self, transformer, visualizer):
        """Test that both exact and heuristic algorithms work end-to-end."""
        message_a = "Hello"
        message_b = "World"
        
        result_exact = transformer.transform(
            message_a, message_b, use_exact=True, respect_ecc=False
        )
        result_heuristic = transformer.transform(
            message_a, message_b, use_exact=False, respect_ecc=False
        )
        
        assert result_exact.success
        assert result_heuristic.success
        
        # Both should produce valid results
        assert result_exact.min_flips >= 0
        assert result_heuristic.min_flips >= 0
        
        # Generate visualizations for both
        qr_a = transformer.encoder.encode(message_a)
        qr_b = transformer.encoder.encode(message_b)
        
        matrix_a = qr_a.module_matrix
        matrix_b = qr_b.module_matrix
        
        if matrix_a.shape != matrix_b.shape:
            min_h = min(matrix_a.shape[0], matrix_b.shape[0])
            min_w = min(matrix_a.shape[1], matrix_b.shape[1])
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
        
        vis_exact = visualizer.create_comparison_grid(
            matrix_a, matrix_b, result_exact.transformed_matrix, result_exact.flip_positions
        )
        vis_heuristic = visualizer.create_comparison_grid(
            matrix_a, matrix_b, result_heuristic.transformed_matrix, result_heuristic.flip_positions
        )
        
        assert vis_exact is not None
        assert vis_heuristic is not None

