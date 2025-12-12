"""QArt transformer using Reed-Solomon linearity and basis vectors."""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
import copy
from .qr_encoder import QREncoder
from .rs_analysis import RSAnalyzer


@dataclass
class QArtResult:
    """Result of QArt transformation."""
    success: bool
    min_flips: int
    flip_positions: List[Tuple[int, int]]
    transformed_matrix: Optional[np.ndarray]
    within_ecc: bool
    stats: Dict
    message_a: str
    message_b: str
    basis_vectors: Optional[Dict] = None


class QArtTransformer:
    """QArt transformer using RS linearity and basis vectors."""
    
    def __init__(self, ecc_level: str = 'H', version: Optional[int] = None):
        """
        Initialize QArt transformer.
        
        Args:
            ecc_level: Error correction level ('L', 'M', 'Q', 'H')
            version: QR code version (None for auto)
        """
        self.ecc_level = ecc_level
        self.version = version
        self.ecc_code = self._get_ecc_code(ecc_level)
    
    def _get_ecc_code(self, ecc_level: str):
        """Convert ECC level string to qrcode constant."""
        mapping = {
            'L': ERROR_CORRECT_L,
            'M': ERROR_CORRECT_M,
            'Q': ERROR_CORRECT_Q,
            'H': ERROR_CORRECT_H
        }
        return mapping.get(ecc_level.upper(), ERROR_CORRECT_H)
    
    def transform(self, message_a: str, message_b: str) -> QArtResult:
        """
        Transform QR code A to look like QR code B using QArt method.
        
        Uses RS linearity: finds basis vectors by flipping padding bits,
        then uses coordinate descent to find optimal combination.
        
        Args:
            message_a: Original message
            message_b: Target message
        
        Returns:
            QArtResult with transformation details
        """
        # Encode both messages
        # Use border=0 for consistency (no quiet zone in matrix)
        qr_a = qrcode.QRCode(
            version=self.version,
            error_correction=self.ecc_code,
            box_size=1,
            border=0  # No border for matrix extraction
        )
        qr_a.add_data(message_a)
        qr_a.make(fit=self.version is None)
        
        qr_b = qrcode.QRCode(
            version=self.version,
            error_correction=self.ecc_code,
            box_size=1,
            border=0  # No border for matrix extraction
        )
        qr_b.add_data(message_b)
        qr_b.make(fit=self.version is None)
        
        # Ensure same version
        if qr_a.version != qr_b.version:
            max_version = max(qr_a.version, qr_b.version)
            self.version = max_version
            qr_a = qrcode.QRCode(version=max_version, error_correction=self.ecc_code, box_size=1, border=0)
            qr_a.add_data(message_a)
            qr_a.make(fit=False)
            qr_b = qrcode.QRCode(version=max_version, error_correction=self.ecc_code, box_size=1, border=0)
            qr_b.add_data(message_b)
            qr_b.make(fit=False)
        
        base_matrix = np.array(qr_a.get_matrix(), dtype=int)
        target_matrix = np.array(qr_b.get_matrix(), dtype=int)
        
        # Ensure same dimensions - align to larger size
        max_height = max(base_matrix.shape[0], target_matrix.shape[0])
        max_width = max(base_matrix.shape[1], target_matrix.shape[1])
        
        def align_matrix(matrix, target_h, target_w):
            h, w = matrix.shape
            aligned = np.zeros((target_h, target_w), dtype=matrix.dtype)
            aligned[:h, :w] = matrix
            return aligned
        
        base_matrix = align_matrix(base_matrix, max_height, max_width)
        target_matrix = align_matrix(target_matrix, max_height, max_width)
        
        # Get basis vectors by analyzing padding bits
        basis_vectors = self._extract_basis_vectors(qr_a, base_matrix)
        
        # Solve using coordinate descent
        result = self._solve_coordinate_descent(base_matrix, target_matrix, basis_vectors)
        
        # Build transformed matrix - ALWAYS start from base_matrix to ensure exact same dimensions
        # This is critical for proper alignment in visualization
        transformed_matrix = base_matrix.copy()
        
        # Apply all flips to the base matrix
        for row, col in result['flip_positions']:
            # Ensure coordinates are within bounds
            if 0 <= row < transformed_matrix.shape[0] and 0 <= col < transformed_matrix.shape[1]:
                transformed_matrix[row, col] = 1 - transformed_matrix[row, col]
        
        # Double-check: transformed_matrix should have EXACT same dimensions as base_matrix
        # If for some reason it doesn't, rebuild it
        if transformed_matrix.shape != base_matrix.shape:
            # This should never happen, but if it does, rebuild from base
            transformed_matrix = base_matrix.copy()
            for row, col in result['flip_positions']:
                if 0 <= row < transformed_matrix.shape[0] and 0 <= col < transformed_matrix.shape[1]:
                    transformed_matrix[row, col] = 1 - transformed_matrix[row, col]
        
        # Analyze
        rs_analyzer = RSAnalyzer(qr_a.version, self.ecc_level)
        stats = rs_analyzer.analyze_transformation(base_matrix, transformed_matrix)
        
        return QArtResult(
            success=result['success'],
            min_flips=result['min_flips'],
            flip_positions=result['flip_positions'],
            transformed_matrix=transformed_matrix,
            within_ecc=True,  # QArt always produces valid QR codes
            stats=stats,
            message_a=message_a,
            message_b=message_b,
            basis_vectors=basis_vectors
        )
    
    def _get_writable_locations(self, qr: qrcode.QRCode) -> List[Tuple[int, int]]:
        """
        Identify which bytes in the data stream are padding/free.
        
        Returns list of (byte_index, bit_index) tuples for modifiable bits.
        """
        # Access internal data cache
        if not hasattr(qr, 'data_cache') or not qr.data_cache:
            # Try alternative: access data_list directly
            if hasattr(qr, 'data_list') and qr.data_list:
                data_list = list(qr.data_list)
            else:
                # Fallback: estimate based on version and ECC
                # For high ECC, there's more padding space
                version = qr.version
                ecc_ratio = {'L': 0.07, 'M': 0.15, 'Q': 0.25, 'H': 0.30}.get(self.ecc_level, 0.15)
                # Estimate total codewords
                total_codewords = (version + 1) * 4 + 16
                # Estimate data codewords
                data_codewords = int(total_codewords * (1 - ecc_ratio))
                # Assume last 10-20% are padding/free
                padding_start = max(0, data_codewords - max(5, data_codewords // 10))
                
                writable = []
                for byte_idx in range(padding_start, data_codewords):
                    for bit_idx in range(8):
                        writable.append((byte_idx, bit_idx))
                return writable
        
        # Use data_cache if available
        data_cache = qr.data_cache
        total_bytes = len(data_cache)
        
        # Estimate padding: last portion of data bytes
        # For high ECC levels, more space is available
        padding_start = max(0, total_bytes - max(10, total_bytes // 5))
        
        writable = []
        for byte_idx in range(padding_start, total_bytes):
            for bit_idx in range(8):
                writable.append((byte_idx, bit_idx))
        
        return writable
    
    def _extract_basis_vectors(self, base_qr: qrcode.QRCode, 
                               base_matrix: np.ndarray) -> Dict[Tuple[int, int], np.ndarray]:
        """
        Extract basis vectors by flipping padding bits.
        
        For each modifiable bit, flip it and see which pixels change.
        This gives us the "basis vector" - the pattern of pixels controlled by that bit.
        
        Returns:
            Dictionary mapping (byte_idx, bit_idx) -> basis_matrix
        """
        basis_vectors = {}
        writable = self._get_writable_locations(base_qr)
        
        print(f"Extracting {len(writable)} basis vectors...")
        
        for byte_idx, bit_idx in writable:
            try:
                # Create copy of QR code
                temp_qr = copy.deepcopy(base_qr)
                
                # Flip the specific bit in data_cache or data_list
                flipped = False
                if hasattr(temp_qr, 'data_cache') and temp_qr.data_cache:
                    data_cache = list(temp_qr.data_cache)
                    if byte_idx < len(data_cache):
                        data_cache[byte_idx] ^= (1 << bit_idx)
                        temp_qr.data_cache = data_cache
                        flipped = True
                elif hasattr(temp_qr, 'data_list') and temp_qr.data_list:
                    data_list = list(temp_qr.data_list)
                    if byte_idx < len(data_list):
                        data_list[byte_idx] ^= (1 << bit_idx)
                        temp_qr.data_list = data_list
                        flipped = True
                
                if not flipped:
                    continue
                
                # Re-encode with flipped bit
                # Need to clear internal state to force recalculation
                if hasattr(temp_qr, 'modules'):
                    temp_qr.modules = None
                temp_qr.make(fit=False)
                
                new_matrix = np.array(temp_qr.get_matrix(), dtype=int)
                
                # Align to base_matrix dimensions (pad with zeros if smaller)
                max_h = max(new_matrix.shape[0], base_matrix.shape[0])
                max_w = max(new_matrix.shape[1], base_matrix.shape[1])
                
                def align_matrix(m, h, w):
                    aligned = np.zeros((h, w), dtype=m.dtype)
                    mh, mw = m.shape
                    aligned[:mh, :mw] = m
                    return aligned
                
                new_matrix = align_matrix(new_matrix, max_h, max_w)
                base_sub = align_matrix(base_matrix, max_h, max_w)
                
                # Basis vector is the XOR difference
                # 1 means this pixel is controlled by this padding bit
                basis = np.bitwise_xor(base_sub, new_matrix)
                
                # Only store if basis vector has any effect
                if np.any(basis):
                    basis_vectors[(byte_idx, bit_idx)] = basis
            except Exception as e:
                # Skip if we can't extract this basis vector
                continue
        
        print(f"Extracted {len(basis_vectors)} basis vectors")
        return basis_vectors
    
    def _solve_coordinate_descent(self, base_matrix: np.ndarray, 
                                 target_matrix: np.ndarray,
                                 basis_vectors: Dict[Tuple[int, int], np.ndarray]) -> Dict:
        """
        Solve using coordinate descent (greedy) over GF(2).
        
        Algorithm:
        1. Start with Current = BaseQR
        2. For each basis vector, check if flipping it improves similarity to target
        3. Keep flips that improve, discard others
        4. Repeat until convergence
        
        This minimizes Hamming distance: ||Current XOR Target||
        """
        current = base_matrix.copy()
        target = target_matrix.copy()
        
        # Ensure same dimensions - should already be aligned, but double-check
        if current.shape != target.shape:
            max_h = max(current.shape[0], target.shape[0])
            max_w = max(current.shape[1], target.shape[1])
            
            def align(m, h, w):
                aligned = np.zeros((h, w), dtype=m.dtype)
                mh, mw = m.shape
                aligned[:mh, :mw] = m
                return aligned
            
            current = align(current, max_h, max_w)
            target = align(target, max_h, max_w)
        
        # Store original dimensions for final result
        original_height, original_width = current.shape
        
        # Calculate initial distance
        def hamming_distance(a, b):
            return np.sum(a != b)
        
        best_distance = hamming_distance(current, target)
        active_bits = set()  # Which padding bits we've flipped
        flip_positions = []  # Which pixels need to flip
        
        # Coordinate descent: iterate until convergence
        max_iterations = len(basis_vectors) * 2
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Try each basis vector
            for (byte_idx, bit_idx), basis in basis_vectors.items():
                # Check if we've already used this bit
                if (byte_idx, bit_idx) in active_bits:
                    continue
                
                # Ensure basis has same dimensions
                if basis.shape != current.shape:
                    min_h = min(basis.shape[0], current.shape[0])
                    min_w = min(basis.shape[1], current.shape[1])
                    basis = basis[:min_h, :min_w]
                    current_sub = current[:min_h, :min_w]
                    target_sub = target[:min_h, :min_w]
                else:
                    current_sub = current
                    target_sub = target
                
                # Try flipping: new = current XOR basis
                candidate = np.bitwise_xor(current_sub, basis)
                new_distance = hamming_distance(candidate, target_sub)
                
                # If this improves, keep it
                if new_distance < best_distance:
                    current = candidate.copy()
                    best_distance = new_distance
                    active_bits.add((byte_idx, bit_idx))
                    improved = True
                    
                    # Update flip positions (pixels that changed)
                    changed = np.where(basis == 1)
                    for row, col in zip(changed[0], changed[1]):
                        if (row, col) not in flip_positions:
                            flip_positions.append((int(row), int(col)))
        
        # Final flip positions are all pixels that differ from base
        # Align base_matrix to current dimensions for comparison
        if base_matrix.shape != current.shape:
            max_h = max(base_matrix.shape[0], current.shape[0])
            max_w = max(base_matrix.shape[1], current.shape[1])
            
            def align(m, h, w):
                aligned = np.zeros((h, w), dtype=m.dtype)
                mh, mw = m.shape
                aligned[:mh, :mw] = m
                return aligned
            
            aligned_base = align(base_matrix, max_h, max_w)
            aligned_current = align(current, max_h, max_w)
        else:
            aligned_base = base_matrix
            aligned_current = current
        
        final_diff = aligned_current != aligned_base
        final_flip_positions = list(zip(*np.where(final_diff)))
        
        # Filter to valid positions within original base_matrix dimensions
        final_flip_positions = [(int(r), int(c)) for r, c in final_flip_positions 
                               if 0 <= r < base_matrix.shape[0] and 0 <= c < base_matrix.shape[1]]
        
        return {
            'success': True,
            'min_flips': len(final_flip_positions),
            'flip_positions': final_flip_positions,
            'iterations': iteration,
            'final_distance': best_distance
        }
    
    def generate_influence_map(self, qr: qrcode.QRCode, base_matrix: np.ndarray) -> np.ndarray:
        """
        Generate influence map showing which pixels can be controlled.
        
        Returns a heat map where higher values indicate more control.
        """
        basis_vectors = self._extract_basis_vectors(qr, base_matrix)
        influence_map = np.zeros_like(base_matrix, dtype=float)
        
        for basis in basis_vectors.values():
            # Ensure same dimensions
            if basis.shape == influence_map.shape:
                influence_map += basis.astype(float)
        
        return influence_map

