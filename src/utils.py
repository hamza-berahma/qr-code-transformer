"""Utility functions for QR code processing."""

import numpy as np
from typing import Tuple, List, Optional
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H


def get_ecc_level_code(ecc_level: str) -> int:
    """Convert ECC level string to qrcode constant."""
    mapping = {
        'L': ERROR_CORRECT_L,
        'M': ERROR_CORRECT_M,
        'Q': ERROR_CORRECT_Q,
        'H': ERROR_CORRECT_H
    }
    return mapping.get(ecc_level.upper(), ERROR_CORRECT_M)


def get_ecc_capacity(version: int, ecc_level: str) -> int:
    """Get maximum error correction capacity for given version and ECC level.
    
    Returns the maximum number of codewords that can be corrected.
    """
    # QR code error correction capacity table (simplified)
    # Format: (version, ecc_level) -> (total_codewords, ec_codewords_per_block, num_blocks)
    # This is a simplified version - full table is more complex
    capacity_map = {
        (1, 'L'): 7, (1, 'M'): 10, (1, 'Q'): 13, (1, 'H'): 17,
        (2, 'L'): 10, (2, 'M'): 16, (2, 'Q'): 22, (2, 'H'): 28,
        (3, 'L'): 15, (3, 'M'): 26, (3, 'Q'): 36, (3, 'H'): 44,
        # Add more as needed - this is a simplified version
    }
    
    # For versions not in map, estimate based on version
    if (version, ecc_level) in capacity_map:
        return capacity_map[(version, ecc_level)]
    
    # Rough estimation: capacity increases with version
    base_capacity = {
        'L': 7, 'M': 10, 'Q': 13, 'H': 17
    }
    return base_capacity.get(ecc_level.upper(), 10) * version


def matrix_to_image(matrix: np.ndarray, module_size: int = 10) -> 'PIL.Image':
    """Convert binary module matrix to PIL Image."""
    from PIL import Image
    
    height, width = matrix.shape
    img = Image.new('RGB', (width * module_size, height * module_size), 'white')
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            color = (0, 0, 0) if matrix[y, x] == 1 else (255, 255, 255)
            for dy in range(module_size):
                for dx in range(module_size):
                    pixels[x * module_size + dx, y * module_size + dy] = color
    
    return img


def image_to_matrix(image: 'PIL.Image') -> np.ndarray:
    """Convert PIL Image to binary module matrix."""
    import cv2
    
    # Convert to grayscale
    if image.mode != 'L':
        image = image.convert('L')
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Threshold to binary
    _, binary = cv2.threshold(img_array, 127, 1, cv2.THRESH_BINARY_INV)
    
    return binary.astype(np.uint8)

