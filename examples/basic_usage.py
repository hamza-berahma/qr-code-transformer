"""Basic usage example for QR code transformation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transformer import QRTransformer
from src.visualizer import QRVisualizer


def main():
    """Example: Transform QR code from message A to message B."""
    
    # Initialize transformer
    transformer = QRTransformer(ecc_level='M')
    
    # Transform from message A to message B
    print("Transforming QR code from 'Hello' to 'World'...")
    result = transformer.transform(
        message_a="Hello",
        message_b="World",
        use_exact=True,
        respect_ecc=True
    )
    
    print(f"\nTransformation Results:")
    print(f"  Success: {result.success}")
    print(f"  Minimal flips required: {result.min_flips}")
    print(f"  Within ECC capacity: {result.within_ecc}")
    print(f"  Change percentage: {result.stats.get('change_percentage', 0):.2f}%")
    
    # Generate visualization
    visualizer = QRVisualizer(module_size=10)
    
    # Get matrices
    qr_a = transformer.encoder.encode(result.message_a)
    qr_b = transformer.encoder.encode(result.message_b)
    
    matrix_a = qr_a.module_matrix
    matrix_b = qr_b.module_matrix
    
    # Ensure same dimensions
    if matrix_a.shape != matrix_b.shape:
        min_h = min(matrix_a.shape[0], matrix_b.shape[0])
        min_w = min(matrix_a.shape[1], matrix_b.shape[1])
        matrix_a = matrix_a[:min_h, :min_w]
        matrix_b = matrix_b[:min_h, :min_w]
        if result.transformed_matrix is not None:
            result.transformed_matrix = result.transformed_matrix[:min_h, :min_w]
    
    # Create comparison visualization
    comparison = visualizer.create_comparison_grid(
        matrix_a, matrix_b, result.transformed_matrix, result.flip_positions
    )
    
    # Save result
    output_path = Path(__file__).parent / "transformation_result.png"
    comparison.save(output_path)
    print(f"\nVisualization saved to: {output_path}")
    
    # Print flip positions (first 10)
    print(f"\nFirst 10 flip positions (out of {len(result.flip_positions)}):")
    for i, (row, col) in enumerate(result.flip_positions[:10]):
        print(f"  [{i+1}] Row {row}, Col {col}")
    if len(result.flip_positions) > 10:
        print(f"  ... and {len(result.flip_positions) - 10} more")


if __name__ == "__main__":
    main()

