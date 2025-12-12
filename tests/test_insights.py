"""Unit tests for insights generation."""

import pytest
import numpy as np
from src.insights import generate_insights, estimate_data_modules
from src.transformer import TransformationResult
from src.qr_encoder import QREncoder


class TestInsights:
    """Test insights generation."""
    
    def test_generate_insights(self, transformer):
        """Test generating insights from transformation result."""
        result = transformer.transform("Hello", "World", use_exact=True, respect_ecc=False)
        
        qr_a = transformer.encoder.encode(result.message_a)
        qr_b = transformer.encoder.encode(result.message_b)
        
        insights = generate_insights(result, transformer.encoder, qr_a.module_matrix, qr_b.module_matrix)
        
        assert 'transformation_summary' in insights
        assert 'ecc_info' in insights
        assert 'matrix_info' in insights
        assert 'messages' in insights
        assert insights['transformation_summary']['min_flips'] == result.min_flips
    
    def test_estimate_data_modules(self):
        """Test estimating data modules."""
        # Create a sample matrix
        matrix = np.ones((25, 25), dtype=np.uint8)
        data_modules = estimate_data_modules(matrix)
        
        assert data_modules >= 0
        assert data_modules < matrix.size  # Should be less than total
    
    def test_insights_structure(self, transformer):
        """Test insights have correct structure."""
        result = transformer.transform("A", "B", use_exact=True, respect_ecc=False)
        
        qr_a = transformer.encoder.encode(result.message_a)
        qr_b = transformer.encoder.encode(result.message_b)
        
        insights = generate_insights(result, transformer.encoder, qr_a.module_matrix, qr_b.module_matrix)
        
        # Check all required keys exist
        assert 'transformation_summary' in insights
        assert 'ecc_info' in insights
        assert 'matrix_info' in insights
        assert 'messages' in insights
        
        # Check nested structure
        assert 'min_flips' in insights['transformation_summary']
        assert 'level' in insights['ecc_info']
        assert 'size' in insights['matrix_info']
        assert 'original' in insights['messages']
        assert 'target' in insights['messages']

