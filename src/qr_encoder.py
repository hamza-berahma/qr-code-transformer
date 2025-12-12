"""QR code encoding module - encode messages and extract module matrices."""

import numpy as np
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from PIL import Image
from typing import Tuple, Optional, List
import io


class QREncoder:
    """Encodes messages into QR codes and extracts module matrices."""
    
    def __init__(self, ecc_level: str = 'M', version: Optional[int] = None, 
                 box_size: int = 10, border: int = 4):
        """
        Initialize QR encoder.
        
        Args:
            ecc_level: Error correction level ('L', 'M', 'Q', 'H')
            version: QR code version (1-40, None for auto)
            box_size: Module size in pixels
            border: Border thickness in modules
        """
        self.ecc_level = ecc_level
        self.version = version
        self.box_size = box_size
        self.border = border
        self.ecc_code = self._get_ecc_code(ecc_level)
    
    def _get_ecc_code(self, ecc_level: str):
        """Convert ECC level string to qrcode constant."""
        mapping = {
            'L': ERROR_CORRECT_L,
            'M': ERROR_CORRECT_M,
            'Q': ERROR_CORRECT_Q,
            'H': ERROR_CORRECT_H
        }
        return mapping.get(ecc_level.upper(), ERROR_CORRECT_M)
    
    def encode(self, message: str) -> 'QRCodeData':
        """
        Encode a message into a QR code.
        
        Returns:
            QRCodeData object with module matrix and metadata
        """
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.ecc_code,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(message)
        qr.make(fit=True)
        
        # Get the actual version used
        actual_version = qr.version
        
        # Get module matrix
        # Note: get_matrix() includes the border if border > 0
        # We want the matrix without border for consistency
        matrix = qr.get_matrix()
        module_matrix = np.array(matrix, dtype=np.uint8)
        
        # Remove border if present (border adds white modules around the QR code)
        if self.border > 0 and module_matrix.shape[0] > self.border * 2:
            # Remove border from all sides
            module_matrix = module_matrix[self.border:-self.border, self.border:-self.border]
        
        # Get mask pattern (if available)
        mask_pattern = getattr(qr, 'mask_pattern', None)
        
        return QRCodeData(
            message=message,
            module_matrix=module_matrix,
            version=actual_version,
            ecc_level=self.ecc_level,
            mask_pattern=mask_pattern,
            qr_object=qr
        )
    
    def encode_to_image(self, message: str) -> Image.Image:
        """Encode message and return as PIL Image."""
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.ecc_code,
            box_size=self.box_size,
            border=self.border
        )
        qr.add_data(message)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")


class QRCodeData:
    """Container for QR code data and metadata."""
    
    def __init__(self, message: str, module_matrix: np.ndarray, 
                 version: int, ecc_level: str, mask_pattern: Optional[int] = None,
                 qr_object: Optional[qrcode.QRCode] = None):
        self.message = message
        self.module_matrix = module_matrix
        self.version = version
        self.ecc_level = ecc_level
        self.mask_pattern = mask_pattern
        self.qr_object = qr_object
        self.height, self.width = module_matrix.shape
    
    def to_image(self, module_size: int = 10) -> Image.Image:
        """Convert module matrix to PIL Image."""
        height, width = self.module_matrix.shape
        img = Image.new('RGB', (width * module_size, height * module_size), 'white')
        pixels = img.load()
        
        for y in range(height):
            for x in range(width):
                color = (0, 0, 0) if self.module_matrix[y, x] == 1 else (255, 255, 255)
                for dy in range(module_size):
                    for dx in range(module_size):
                        pixels[x * module_size + dx, y * module_size + dy] = color
        
        return img
    
    def get_total_modules(self) -> int:
        """Get total number of modules."""
        return self.height * self.width
    
    def get_data_modules(self) -> int:
        """Estimate number of data modules (excluding finder patterns, timing, etc.)."""
        # Simplified: subtract fixed patterns
        # Finder patterns: 3 * 7*7 = 147 modules
        # Timing patterns: ~2 * (size - 14) modules
        # Format/version info: ~60 modules
        fixed_modules = 147 + 2 * (self.width - 14) + 60
        return max(0, self.get_total_modules() - fixed_modules)

