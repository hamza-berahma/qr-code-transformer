"""Unit tests for visualizer."""

import pytest
import numpy as np
from src.visualizer import QRVisualizer
from src.qr_encoder import QREncoder


class TestQRVisualizer:
    """Test QR visualizer functionality."""
    
    @pytest.fixture
    def visualizer(self):
        """Create a visualizer instance."""
        return QRVisualizer(module_size=10)
    
    @pytest.fixture
    def sample_matrices(self):
        """Create sample matrices for testing."""
        encoder = QREncoder()
        qr_a = encoder.encode("A")
        qr_b = encoder.encode("B")
        return qr_a.module_matrix, qr_b.module_matrix
    
    def test_visualizer_initialization(self, visualizer):
        """Test visualizer can be initialized."""
        assert visualizer is not None
        assert visualizer.module_size == 10
    
    def test_visualize_transformation(self, visualizer, sample_matrices):
        """Test creating transformation visualization."""
        matrix_a, matrix_b = sample_matrices
        
        # Ensure same dimensions
        if matrix_a.shape != matrix_b.shape:
            min_h = min(matrix_a.shape[0], matrix_b.shape[0])
            min_w = min(matrix_a.shape[1], matrix_b.shape[1])
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
        
        # Get differences
        diff = matrix_a != matrix_b
        flip_positions = list(zip(*np.where(diff)))
        
        img = visualizer.visualize_transformation(
            matrix_a, matrix_b, flip_positions, show_flips=True
        )
        
        assert img is not None
        assert img.size[0] > 0
        assert img.size[1] > 0
    
    def test_create_comparison_grid(self, visualizer, sample_matrices):
        """Test creating comparison grid."""
        matrix_a, matrix_b = sample_matrices
        
        # Ensure same dimensions
        if matrix_a.shape != matrix_b.shape:
            min_h = min(matrix_a.shape[0], matrix_b.shape[0])
            min_w = min(matrix_a.shape[1], matrix_b.shape[1])
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
        
        diff = matrix_a != matrix_b
        flip_positions = list(zip(*np.where(diff)))
        transformed = matrix_b.copy()
        
        img = visualizer.create_comparison_grid(
            matrix_a, matrix_b, transformed, flip_positions
        )
        
        assert img is not None
        assert img.size[0] > 0
        assert img.size[1] > 0
    
    def test_generate_heatmap(self, visualizer, sample_matrices):
        """Test generating heatmap."""
        matrix_a, matrix_b = sample_matrices
        
        if matrix_a.shape != matrix_b.shape:
            min_h = min(matrix_a.shape[0], matrix_b.shape[0])
            min_w = min(matrix_a.shape[1], matrix_b.shape[1])
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
        
        diff = matrix_a != matrix_b
        flip_positions = list(zip(*np.where(diff)))
        
        heatmap = visualizer.generate_heatmap(matrix_a, matrix_b, flip_positions)
        
        assert heatmap is not None
        assert heatmap.size[0] > 0
        assert heatmap.size[1] > 0

