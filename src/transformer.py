"""Core transformation algorithm - find minimal changes to transform QR(A) to decode as B."""

import numpy as np
from typing import List, Tuple, Optional, Set, Dict
from dataclasses import dataclass
from .qr_encoder import QREncoder, QRCodeData
from .rs_analysis import RSAnalyzer


@dataclass
class TransformationResult:
    """Result of QR code transformation."""
    success: bool
    min_flips: int
    flip_positions: List[Tuple[int, int]]  # (row, col) positions to flip
    transformed_matrix: Optional[np.ndarray]
    within_ecc: bool  # Whether transformation is within ECC capacity
    stats: Dict
    message_a: str
    message_b: str
    algorithm: str = "unknown"  # Algorithm used: "qart-l", "ilp-h", etc.
    algorithm_results: Optional[Dict] = None  # Results from all algorithms for comparison


class QRTransformer:
    """Transform QR code A to decode as message B with minimal changes using ILP."""
    
    def __init__(self, ecc_level: str = 'M', version: Optional[int] = None):
        """
        Initialize transformer.
        
        Args:
            ecc_level: Error correction level ('L', 'M', 'Q', 'H') - used as default only
            version: QR code version (None for auto)
        """
        self.ecc_level = ecc_level
        self.version = version
        self.encoder = QREncoder(ecc_level=ecc_level, version=version)
        # Note: Individual transformers are created per ECC level in transform()
    
    def transform(self, message_a: str, message_b: str, 
                 use_exact: bool = True, respect_ecc: bool = True,
                 use_ilp: bool = True) -> TransformationResult:
        """
        Transform QR code encoding message A to decode as message B.
        
        AUTOMATICALLY tests all 4 ECC levels (L, M, Q, H) with both QArt and ILP algorithms,
        then selects the combination that gives the minimum module squares to change.
        
        This ensures optimal results by:
        - Testing all ECC levels: L (~7%), M (~15%), Q (~25%), H (~30%)
        - Testing both algorithms: QArt (RS Linearity) and ILP (Integer Linear Programming)
        - Selecting the best combination (up to 8 total combinations tested)
        
        Args:
            message_a: Original message
            message_b: Target message
            use_exact: (Deprecated, kept for compatibility)
            respect_ecc: (Deprecated, kept for compatibility)
            use_ilp: (Deprecated, kept for compatibility)
        
        Returns:
            TransformationResult with minimal flip positions from the best ECC level + algorithm.
            The result includes algorithm_results dict showing performance of all combinations.
        """
        ecc_levels = ['L', 'M', 'Q', 'H']
        all_results = []
        all_algorithm_results = {}
        
        # Test all ECC levels with all algorithms (QArt, ILP, Hybrid)
        for ecc_level in ecc_levels:
            # Try QArt algorithm for this ECC level
            try:
                from .qart_transformer import QArtTransformer
                qart_transformer = QArtTransformer(ecc_level=ecc_level, version=self.version)
                qart_result = qart_transformer.transform(message_a, message_b)
                result = TransformationResult(
                    success=qart_result.success,
                    min_flips=qart_result.min_flips,
                    flip_positions=qart_result.flip_positions,
                    transformed_matrix=qart_result.transformed_matrix,
                    within_ecc=qart_result.within_ecc,
                    stats=qart_result.stats,
                    message_a=qart_result.message_a,
                    message_b=qart_result.message_b,
                    algorithm=f"qart-{ecc_level.lower()}"
                )
                all_results.append(result)
                key = f"qart-{ecc_level.lower()}"
                all_algorithm_results[key] = {
                    "min_flips": qart_result.min_flips,
                    "success": qart_result.success,
                    "within_ecc": qart_result.within_ecc,
                    "ecc_level": ecc_level
                }
            except Exception as e:
                all_algorithm_results[f"qart-{ecc_level.lower()}"] = {"error": str(e), "ecc_level": ecc_level}
            
            # Try Hybrid algorithm for this ECC level
            try:
                from .hybrid_transformer import HybridTransformer
                hybrid_transformer = HybridTransformer(ecc_level=ecc_level, version=self.version)
                hybrid_result = hybrid_transformer.transform(message_a, message_b)
                result = TransformationResult(
                    success=hybrid_result.success,
                    min_flips=hybrid_result.min_flips,
                    flip_positions=hybrid_result.flip_positions,
                    transformed_matrix=hybrid_result.transformed_matrix,
                    within_ecc=hybrid_result.within_ecc,
                    stats=hybrid_result.stats,
                    message_a=hybrid_result.message_a,
                    message_b=hybrid_result.message_b,
                    algorithm=f"hybrid-{ecc_level.lower()}"
                )
                all_results.append(result)
                key = f"hybrid-{ecc_level.lower()}"
                all_algorithm_results[key] = {
                    "min_flips": hybrid_result.min_flips,
                    "success": hybrid_result.success,
                    "within_ecc": hybrid_result.within_ecc,
                    "ecc_level": ecc_level,
                    "padding_flips": hybrid_result.padding_flips,
                    "error_injection_flips": hybrid_result.error_injection_flips
                }
            except Exception as e:
                all_algorithm_results[f"hybrid-{ecc_level.lower()}"] = {"error": str(e), "ecc_level": ecc_level}
            
            # Try ILP algorithm for this ECC level
            try:
                from .ilp_transformer import ILPQRTransformer
                ilp_transformer = ILPQRTransformer(ecc_level=ecc_level, version=self.version)
                ilp_result = ilp_transformer.transform(message_a, message_b)
                result = TransformationResult(
                    success=ilp_result.success,
                    min_flips=ilp_result.min_flips,
                    flip_positions=ilp_result.flip_positions,
                    transformed_matrix=ilp_result.transformed_matrix,
                    within_ecc=ilp_result.within_ecc,
                    stats=ilp_result.stats,
                    message_a=ilp_result.message_a,
                    message_b=ilp_result.message_b,
                    algorithm=f"ilp-{ecc_level.lower()}"
                )
                all_results.append(result)
                key = f"ilp-{ecc_level.lower()}"
                all_algorithm_results[key] = {
                    "min_flips": ilp_result.min_flips,
                    "success": ilp_result.success,
                    "within_ecc": ilp_result.within_ecc,
                    "ecc_level": ecc_level,
                    "solver_time": getattr(ilp_result, 'solver_time', 0.0)
                }
            except Exception as e:
                all_algorithm_results[f"ilp-{ecc_level.lower()}"] = {"error": str(e), "ecc_level": ecc_level}
        
        # Select the best result (minimum flips) across all ECC levels and algorithms
        if not all_results:
            raise RuntimeError("No transformer available. Please install required dependencies.")
        
        # Filter successful results
        successful_results = [r for r in all_results if r.success]
        
        if not successful_results:
            # If no successful results, return the first one (with error info)
            best_result = all_results[0]
            best_result.algorithm_results = all_algorithm_results
            return best_result
        
        # Find result with minimum flips - this ensures we always get the best solution
        best_result = min(successful_results, key=lambda r: r.min_flips)
        best_result.algorithm_results = all_algorithm_results
        
        # Extract ECC level and algorithm from algorithm name
        if '-' in best_result.algorithm:
            parts = best_result.algorithm.split('-')
            best_ecc = parts[1].upper()
            best_algo = parts[0]
        else:
            best_ecc = self.ecc_level
            best_algo = best_result.algorithm
        
        best_result.stats['best_ecc_level'] = best_ecc
        best_result.stats['best_algorithm'] = best_algo
        
        return best_result
    
    def _transform_exact(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                        rs_analyzer: RSAnalyzer, respect_ecc: bool) -> Dict:
        """Deprecated: Use ILP transformer instead."""
        """
        Exact algorithm: find optimal minimal transformation.
        
        ALWAYS exploits RS non-bijectivity to minimize flips:
        - Since matrix_b decodes to message B, we can flip up to ECC capacity 
          modules in matrix_b and it still decodes to B
        - So we minimize flips in A by exploiting ECC capacity
        
        The respect_ecc flag only controls whether we allow solutions exceeding capacity.
        """
        ecc_capacity = rs_analyzer.ecc_capacity
        diff = matrix_a != matrix_b
        diff_positions = list(zip(*np.where(diff)))
        total_differences = len(diff_positions)
        
        # ALWAYS exploit ECC to minimize: we can "absorb" up to ecc_capacity
        # differences by exploiting that B has error correction room
        min_flips_needed = max(0, total_differences - ecc_capacity)
        
        # Check if solution is within ECC capacity
        within_ecc = min_flips_needed == 0 or total_differences <= ecc_capacity
        
        if respect_ecc and not within_ecc:
            # Solution exceeds ECC capacity and we're respecting it
            return {
                'success': False,
                'min_flips': min_flips_needed,
                'flip_positions': diff_positions[ecc_capacity:],
                'note': f'Solution requires {min_flips_needed} flips, exceeding ECC capacity of {ecc_capacity}'
            }
        
        # Return minimized solution (exploiting ECC)
        return {
            'success': True,
            'min_flips': min_flips_needed,
            'flip_positions': diff_positions[ecc_capacity:] if total_differences > ecc_capacity else diff_positions,
            'note': f'Exploited ECC: {min(ecc_capacity, total_differences)} differences handled via error correction'
        }
    
    
    def _transform_heuristic(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                           rs_analyzer: RSAnalyzer, respect_ecc: bool) -> Dict:
        """Deprecated: Use ILP transformer instead."""
        """
        Heuristic algorithm: faster approximate solution.
        
        Uses the same ECC exploitation strategy as exact algorithm.
        For future improvement, could use:
        - Prioritize flipping modules in data regions vs fixed patterns
        - Use RS block structure to find equivalent patterns
        - Iterative improvement with local search
        """
        # Use same ECC exploitation as exact (it's already efficient)
        return self._transform_exact(matrix_a, matrix_b, rs_analyzer, respect_ecc)
    
    def transform_from_image(self, image_path: str, message_b: str,
                            use_exact: bool = True, respect_ecc: bool = True,
                            use_ilp: bool = True) -> TransformationResult:
        """
        Transform an existing QR code image to decode as message_b.
        Runs both algorithms and returns the best result.
        
        Args:
            image_path: Path to QR code image
            message_b: Target message
            use_exact: (Deprecated, kept for compatibility)
            respect_ecc: (Deprecated, kept for compatibility)
            use_ilp: (Deprecated, kept for compatibility)
        
        Returns:
            TransformationResult with best algorithm result
        """
        from PIL import Image
        from .utils import image_to_matrix
        
        # Load and decode image
        img = Image.open(image_path)
        matrix_a = image_to_matrix(img)
        
        # For image-based transformation, test all ECC levels
        ecc_levels = ['L', 'M', 'Q', 'H']
        all_results = []
        all_algorithm_results = {}
        
        for ecc_level in ecc_levels:
            # Encode target message with this ECC level
            encoder = QREncoder(ecc_level=ecc_level, version=self.version)
            qr_b = encoder.encode(message_b)
            matrix_b = qr_b.module_matrix
            
            # Match dimensions
            if matrix_a.shape != matrix_b.shape:
                min_h = min(matrix_a.shape[0], matrix_b.shape[0])
                min_w = min(matrix_a.shape[1], matrix_b.shape[1])
                matrix_a_aligned = matrix_a[:min_h, :min_w]
                matrix_b_aligned = matrix_b[:min_h, :min_w]
            else:
                matrix_a_aligned = matrix_a
                matrix_b_aligned = matrix_b
            
            # Try ILP algorithm for this ECC level
            try:
                from .ilp_transformer import ILPQRTransformer
                ilp_transformer = ILPQRTransformer(ecc_level=ecc_level, version=self.version)
                estimated_version = max(1, (matrix_a_aligned.shape[0] - 21) // 4 + 1)
                rs_analyzer = RSAnalyzer(estimated_version, ecc_level)
                ilp_result = ilp_transformer._solve_ilp(matrix_a_aligned, matrix_b_aligned, rs_analyzer)
                
                transformed_matrix = matrix_a_aligned.copy()
                for row, col in ilp_result['flip_positions']:
                    if 0 <= row < transformed_matrix.shape[0] and 0 <= col < transformed_matrix.shape[1]:
                        transformed_matrix[row, col] = 1 - transformed_matrix[row, col]
                
                stats = rs_analyzer.analyze_transformation(matrix_a_aligned, transformed_matrix)
                
                result = TransformationResult(
                    success=ilp_result['success'],
                    min_flips=ilp_result['min_flips'],
                    flip_positions=ilp_result['flip_positions'],
                    transformed_matrix=transformed_matrix,
                    within_ecc=stats['within_ecc_capacity'],
                    stats=stats,
                    message_a='[from image]',
                    message_b=message_b,
                    algorithm=f"ilp-{ecc_level.lower()}"
                )
                all_results.append(result)
                key = f"ilp-{ecc_level.lower()}"
                all_algorithm_results[key] = {
                    "min_flips": ilp_result['min_flips'],
                    "success": ilp_result['success'],
                    "within_ecc": stats['within_ecc_capacity'],
                    "ecc_level": ecc_level,
                    "solver_time": ilp_result.get('solver_time', 0.0)
                }
            except Exception as e:
                all_algorithm_results[f"ilp-{ecc_level.lower()}"] = {"error": str(e), "ecc_level": ecc_level}
        
        # Select best result
        if not all_results:
            raise RuntimeError("No transformer available. Please install ortools: pip install ortools")
        
        successful_results = [r for r in all_results if r.success]
        if not successful_results:
            best_result = all_results[0]
            best_result.algorithm_results = all_algorithm_results
            return best_result
        
        best_result = min(successful_results, key=lambda r: r.min_flips)
        best_result.algorithm_results = all_algorithm_results
        
        # Extract ECC level
        if '-' in best_result.algorithm:
            best_ecc = best_result.algorithm.split('-')[1].upper()
            best_algo = best_result.algorithm.split('-')[0]
        else:
            best_ecc = self.ecc_level
            best_algo = best_result.algorithm
        
        best_result.stats['best_ecc_level'] = best_ecc
        best_result.stats['best_algorithm'] = best_algo
        
        return best_result
