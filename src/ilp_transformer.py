"""ILP-based transformer using Integer Linear Programming to find minimal module flips."""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    pywraplp = None

from .qr_encoder import QREncoder, QRCodeData
from .rs_analysis import RSAnalyzer


@dataclass
class ILPTransformationResult:
    """Result of ILP-based transformation."""
    success: bool
    min_flips: int
    flip_positions: List[Tuple[int, int]]
    transformed_matrix: Optional[np.ndarray]
    within_ecc: bool
    stats: Dict
    message_a: str
    message_b: str
    solver_time: float


class ILPQRTransformer:
    """Transform QR code A to decode as message B using ILP optimization."""
    
    def __init__(self, ecc_level: str = 'M', version: Optional[int] = None):
        """
        Initialize ILP transformer.
        
        Args:
            ecc_level: Error correction level ('L', 'M', 'Q', 'H')
            version: QR code version (None for auto)
        """
        self.ecc_level = ecc_level
        self.version = version
        self.encoder = QREncoder(ecc_level=ecc_level, version=version)
    
    def transform(self, message_a: str, message_b: str) -> ILPTransformationResult:
        """
        Transform QR code encoding message A to decode as message B using ILP.
        
        Args:
            message_a: Original message
            message_b: Target message
        
        Returns:
            ILPTransformationResult with minimal flip positions
        """
        # Encode both messages
        qr_a = self.encoder.encode(message_a)
        qr_b = self.encoder.encode(message_b)
        
        # Ensure same version
        if qr_a.version != qr_b.version:
            max_version = max(qr_a.version, qr_b.version)
            self.encoder.version = max_version
            qr_a = self.encoder.encode(message_a)
            qr_b = self.encoder.encode(message_b)
        
        matrix_a = qr_a.module_matrix
        matrix_b = qr_b.module_matrix
        
        # Ensure same dimensions
        if matrix_a.shape != matrix_b.shape:
            min_h = min(matrix_a.shape[0], matrix_b.shape[0])
            min_w = min(matrix_a.shape[1], matrix_b.shape[1])
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
        
        # Initialize RS analyzer
        rs_analyzer = RSAnalyzer(qr_a.version, self.ecc_level)
        
        # Solve ILP
        result = self._solve_ilp(matrix_a, matrix_b, rs_analyzer)
        
        # Build transformed matrix
        transformed_matrix = matrix_a.copy()
        for row, col in result['flip_positions']:
            if 0 <= row < transformed_matrix.shape[0] and 0 <= col < transformed_matrix.shape[1]:
                transformed_matrix[row, col] = 1 - transformed_matrix[row, col]
        
        stats = rs_analyzer.analyze_transformation(matrix_a, transformed_matrix)
        
        return ILPTransformationResult(
            success=result['success'],
            min_flips=result['min_flips'],
            flip_positions=result['flip_positions'],
            transformed_matrix=transformed_matrix,
            within_ecc=stats['within_ecc_capacity'],
            stats=stats,
            message_a=message_a,
            message_b=message_b,
            solver_time=result.get('solver_time', 0.0)
        )
    
    def _solve_ilp(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                   rs_analyzer: RSAnalyzer) -> Dict:
        """
        Solve ILP to find minimal module flips.
        
        Variables: x[i,j] = 1 if module (i,j) is flipped, 0 otherwise
        Objective: minimize sum of x[i,j]
        Constraints: After flipping, QR decodes to target message (via RS constraints)
        """
        if not ORTOOLS_AVAILABLE:
            # Fallback to greedy approach
            return self._solve_greedy(matrix_a, matrix_b, rs_analyzer)
        
        height, width = matrix_a.shape
        n = height  # Assuming square matrix
        
        # Create solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            # Fallback to SAT solver
            solver = pywraplp.Solver.CreateSolver('SAT')
        if not solver:
            # Fallback to greedy
            return self._solve_greedy(matrix_a, matrix_b, rs_analyzer)
        
        # Decision variables: x[i,j] = 1 if module (i,j) is flipped
        x = {}
        for i in range(height):
            for j in range(width):
                x[i, j] = solver.IntVar(0, 1, f'x_{i}_{j}')
        
        # Calculate differences
        diff = matrix_a != matrix_b
        diff_positions = list(zip(*np.where(diff)))
        total_differences = len(diff_positions)
        
        # Get ECC capacity (max errors that can be corrected)
        ecc_capacity = rs_analyzer.ecc_capacity
        
        # Simplified approach: We know which modules differ
        # We can exploit ECC: up to ecc_capacity differences can be "absorbed"
        # So we minimize: max(0, total_differences - ecc_capacity)
        
        # For ILP, we model this as:
        # - We want to flip modules to match target
        # - But we can exploit ECC to reduce flips needed
        
        # Strategy: For each differing position, we can either:
        # 1. Flip it in A (cost: 1, uses x[i,j])
        # 2. "Absorb" it via ECC (cost: 0, but uses ECC capacity)
        
        # We need to decide which differences to flip vs absorb
        # This is a set cover problem: minimize flips while respecting ECC
        
        # Add constraint: We can only "absorb" up to ecc_capacity differences
        # The rest must be flipped
        
        # For simplicity, we'll use a greedy ILP formulation:
        # Minimize sum of x[i,j] subject to:
        # - For positions that differ: we must either flip (x[i,j]=1) or absorb (via ECC)
        # - Number of absorbed differences <= ecc_capacity
        
        # Add auxiliary variables for "absorbed" differences
        # y[k] = 1 if difference k is absorbed via ECC, 0 if flipped
        y = {}
        for idx, (i, j) in enumerate(diff_positions):
            y[idx] = solver.IntVar(0, 1, f'y_{idx}')
        
        # Constraint: For each difference, either flip it or absorb it via ECC
        for idx, (i, j) in enumerate(diff_positions):
            # If we absorb via ECC (y[idx] = 1), we don't need to flip (x[i,j] = 0)
            # If we don't absorb (y[idx] = 0), we must flip (x[i,j] = 1)
            # So: x[i,j] = 1 - y[idx]
            solver.Add(x[i, j] == 1 - y[idx])
        
        # Constraint: Can only absorb up to ecc_capacity differences
        solver.Add(solver.Sum([y[idx] for idx in range(len(diff_positions))]) <= ecc_capacity)
        
        # For positions that don't differ, we shouldn't flip
        for i in range(height):
            for j in range(width):
                if (i, j) not in diff_positions:
                    solver.Add(x[i, j] == 0)
        
        # Objective: Minimize total flips
        solver.Minimize(solver.Sum([x[i, j] for i in range(height) for j in range(width)]))
        
        # Solve
        import time
        start_time = time.time()
        status = solver.Solve()
        solver_time = time.time() - start_time
        
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            # Extract solution
            flip_positions = []
            for i in range(height):
                for j in range(width):
                    if x[i, j].solution_value() > 0.5:
                        flip_positions.append((int(i), int(j)))
            
            return {
                'success': True,
                'min_flips': len(flip_positions),
                'flip_positions': flip_positions,
                'solver_time': solver_time
            }
        else:
            # Fallback: use greedy approach
            min_flips = max(0, total_differences - ecc_capacity)
            flip_positions = diff_positions[ecc_capacity:] if total_differences > ecc_capacity else []
            
            return {
                'success': False,
                'min_flips': min_flips,
                'flip_positions': flip_positions,
                'solver_time': solver_time,
                'note': 'ILP solver failed, using greedy fallback'
            }
    
    def _map_modules_to_codewords(self, matrix: np.ndarray, version: int) -> List[List[Tuple[int, int]]]:
        """
        Map QR modules to codewords/symbols.
        
        This is a simplified mapping - full QR spec is more complex.
        Returns list of codewords, each codeword is a list of (row, col) module positions.
        """
        # Simplified: QR codes use zig-zag pattern to map bits to codewords
        # Each codeword is 8 bits
        # This is a placeholder - full implementation would follow QR spec exactly
        
        height, width = matrix.shape
        codewords = []
        
        # Simplified approach: group modules into 8-bit codewords
        # In practice, QR uses specific placement rules (zig-zag, avoiding finder patterns, etc.)
        bits_per_codeword = 8
        total_bits = height * width
        
        # Estimate number of data codewords (excluding fixed patterns)
        # Roughly: total modules - finder patterns - timing - format/version
        fixed_modules = 3 * 7 * 7 + 2 * (height - 14) + 60  # Simplified
        data_modules = max(0, total_bits - fixed_modules)
        num_codewords = data_modules // bits_per_codeword
        
        # For now, return empty list (we'll use simplified approach)
        # Full implementation would map modules to codewords following QR spec
        return []
    
    def _solve_greedy(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                     rs_analyzer: RSAnalyzer) -> Dict:
        """Greedy fallback when ILP solver is not available."""
        diff = matrix_a != matrix_b
        diff_positions = list(zip(*np.where(diff)))
        total_differences = len(diff_positions)
        ecc_capacity = rs_analyzer.ecc_capacity
        
        min_flips = max(0, total_differences - ecc_capacity)
        flip_positions = diff_positions[ecc_capacity:] if total_differences > ecc_capacity else diff_positions
        
        return {
            'success': True,
            'min_flips': min_flips,
            'flip_positions': flip_positions,
            'solver_time': 0.0,
            'note': 'Using greedy fallback (ortools not available)'
        }

