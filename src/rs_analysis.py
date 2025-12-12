"""Reed-Solomon error correction analysis for QR codes."""

import numpy as np
from typing import List, Tuple, Optional, Set
from reedsolo import RSCodec
import qrcode


class RSAnalyzer:
    """Analyze Reed-Solomon error correction in QR codes."""
    
    def __init__(self, version: int, ecc_level: str):
        """
        Initialize RS analyzer.
        
        Args:
            version: QR code version (1-40)
            ecc_level: Error correction level ('L', 'M', 'Q', 'H')
        """
        self.version = version
        self.ecc_level = ecc_level.upper()
        self.ecc_capacity = self._get_ecc_capacity()
        self.total_codewords = self._get_total_codewords()
        # Calculate EC codewords first (simplified estimation)
        # EC codewords are roughly proportional to ECC level
        # This must be calculated before calling _get_data_codewords()
        ec_codewords_map = {'L': 0.07, 'M': 0.15, 'Q': 0.25, 'H': 0.30}
        ec_ratio = ec_codewords_map.get(self.ecc_level, 0.15)
        self.ec_codewords = int(self.total_codewords * ec_ratio)
        # Now we can calculate data codewords
        self.data_codewords = self.total_codewords - self.ec_codewords
    
    def _get_ecc_capacity(self) -> int:
        """Get maximum number of errors that can be corrected."""
        # Simplified capacity table - full implementation would use complete QR spec
        # This is the number of codewords that can be corrected
        capacity_map = {
            (1, 'L'): 7, (1, 'M'): 10, (1, 'Q'): 13, (1, 'H'): 17,
            (2, 'L'): 10, (2, 'M'): 16, (2, 'Q'): 22, (2, 'H'): 28,
            (3, 'L'): 15, (3, 'M'): 26, (3, 'Q'): 36, (3, 'H'): 44,
            (4, 'L'): 20, (4, 'M'): 36, (4, 'Q'): 52, (4, 'H'): 64,
            (5, 'L'): 26, (5, 'M'): 48, (5, 'Q'): 72, (5, 'H'): 88,
        }
        
        if (self.version, self.ecc_level) in capacity_map:
            return capacity_map[(self.version, self.ecc_level)]
        
        # Estimate for higher versions
        base = {'L': 7, 'M': 10, 'Q': 13, 'H': 17}[self.ecc_level]
        return int(base * (1 + (self.version - 1) * 0.5))
    
    def _get_total_codewords(self) -> int:
        """Get total number of codewords for this version."""
        # Simplified: total codewords = (version + 1) * 4 + 16
        return (self.version + 1) * 4 + 16
    
    def _get_data_codewords(self) -> int:
        """Get number of data codewords (excluding ECC)."""
        # This is now calculated in __init__ to avoid circular dependency
        # Return a simplified estimation if called before initialization
        if hasattr(self, 'ec_codewords'):
            return self.total_codewords - self.ec_codewords
        # Fallback estimation
        ec_codewords_map = {'L': 0.07, 'M': 0.15, 'Q': 0.25, 'H': 0.30}
        ec_ratio = ec_codewords_map.get(self.ecc_level, 0.15)
        ec_codewords = int(self.total_codewords * ec_ratio)
        return self.total_codewords - ec_codewords
    
    def can_correct_errors(self, num_errors: int) -> bool:
        """Check if given number of errors can be corrected."""
        return num_errors <= self.ecc_capacity
    
    def get_valid_patterns(self, target_message: str, 
                          reference_matrix: np.ndarray) -> List[np.ndarray]:
        """
        Find valid QR code patterns that decode to target_message.
        
        This exploits the non-bijective nature of RS: multiple patterns decode to same message.
        Returns a list of valid module matrices.
        """
        # Strategy: Generate QR for target, then find variations within ECC capacity
        valid_patterns = []
        
        # First, get the canonical QR for target message
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self._get_ecc_code(),
            box_size=1,
            border=0
        )
        qr.add_data(target_message)
        qr.make(fit=False)  # Use exact version
        
        canonical_matrix = np.array(qr.get_matrix(), dtype=np.uint8)
        valid_patterns.append(canonical_matrix)
        
        # Find alternative patterns by flipping modules within ECC capacity
        # This is a simplified approach - full implementation would be more sophisticated
        max_flips = min(self.ecc_capacity, reference_matrix.size // 10)  # Limit search
        
        # Generate variations by flipping small sets of modules
        # In practice, this would need more sophisticated search
        for num_flips in range(1, max_flips + 1):
            # This is a placeholder - actual implementation would use smarter search
            # For now, we'll generate patterns in the transformer module
            pass
        
        return valid_patterns
    
    def _get_ecc_code(self):
        """Get qrcode ECC constant."""
        from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
        mapping = {
            'L': ERROR_CORRECT_L,
            'M': ERROR_CORRECT_M,
            'Q': ERROR_CORRECT_Q,
            'H': ERROR_CORRECT_H
        }
        return mapping.get(self.ecc_level, ERROR_CORRECT_M)
    
    def analyze_transformation(self, matrix_a: np.ndarray, matrix_b: np.ndarray) -> dict:
        """
        Analyze the transformation from matrix_a to matrix_b.
        
        Returns statistics about the transformation.
        """
        diff = matrix_a != matrix_b
        num_changes = np.sum(diff)
        change_percentage = (num_changes / matrix_a.size) * 100
        
        return {
            'num_changes': int(num_changes),
            'change_percentage': change_percentage,
            'within_ecc_capacity': self.can_correct_errors(num_changes),
            'ecc_capacity': self.ecc_capacity,
            'total_modules': matrix_a.size,
            'data_modules': matrix_a.size  # Simplified
        }

