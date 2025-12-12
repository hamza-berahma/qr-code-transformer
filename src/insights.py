"""Generate insights and statistics about QR transformations."""

from typing import Dict, List
from .transformer import TransformationResult
from .qr_encoder import QREncoder
import numpy as np


def generate_insights(result: TransformationResult, encoder: QREncoder,
                     matrix_a: np.ndarray, matrix_b: np.ndarray) -> Dict:
    """
    Generate detailed insights about the transformation.
    
    Returns:
        Dictionary with insights and statistics
    """
    insights = {
        "transformation_summary": {
            "min_flips": result.min_flips,  # Number of module squares that need to be changed
            "within_ecc": result.within_ecc,
            "success": result.success
        },
        "ecc_info": {
            "level": encoder.ecc_level,
            "capacity": result.stats.get('ecc_capacity', 0),
            "utilization": (result.min_flips / result.stats.get('ecc_capacity', 1) * 100) 
                          if result.stats.get('ecc_capacity', 0) > 0 else 0
        },
        "matrix_info": {
            "size": f"{matrix_a.shape[0]}x{matrix_a.shape[1]}",
            "total_modules": int(matrix_a.size),
            "data_modules": estimate_data_modules(matrix_a),
            "change_percentage": result.stats.get('change_percentage', 0)
        },
        "messages": {
            "original": result.message_a,
            "target": result.message_b,
            "length_diff": len(result.message_b) - len(result.message_a)
        },
        "recommendations": generate_recommendations(result)
    }
    
    return insights


def estimate_data_modules(matrix: np.ndarray) -> int:
    """Estimate number of data modules (excluding fixed patterns)."""
    size = matrix.shape[0]
    # Simplified: subtract finder patterns, timing, format/version info
    finder_modules = 3 * 7 * 7  # 3 finder patterns
    timing_modules = 2 * (size - 14)  # Timing patterns
    format_modules = 60  # Format and version info
    return max(0, matrix.size - finder_modules - timing_modules - format_modules)


def generate_recommendations(result: TransformationResult) -> List[str]:
    """Generate recommendations based on transformation result."""
    recommendations = []
    
    if not result.within_ecc:
        recommendations.append(
            f"Transformation requires {result.min_flips} flips, exceeding ECC capacity. "
            "Consider using a higher ECC level (Q or H) or shorter messages."
        )
    
    if result.min_flips > 50:
        recommendations.append(
            "Large number of flips required. The transformation may not be practical."
        )
    
    if result.within_ecc and result.min_flips < 10:
        recommendations.append(
            "Transformation is well within ECC capacity. This is a good candidate for "
            "exploiting RS non-bijectivity."
        )
    
    if not recommendations:
        recommendations.append("Transformation looks feasible.")
    
    return recommendations

