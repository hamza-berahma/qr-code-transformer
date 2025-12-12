"""Visualization module for QR code transformations."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional, Union
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent display issues
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO


class QRVisualizer:
    """Visualize QR code transformations and differences."""
    
    def __init__(self, module_size: int = 10):
        """
        Initialize visualizer.
        
        Args:
            module_size: Size of each module in pixels
        """
        self.module_size = module_size
    
    def visualize_transformation(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                                flip_positions: List[Tuple[int, int]],
                                show_flips: bool = True) -> Image.Image:
        """
        Create visualization showing transformation from A to B.
        
        Args:
            matrix_a: Original matrix
            matrix_b: Target matrix
            flip_positions: List of (row, col) positions that need to flip
            show_flips: Highlight flip positions
        
        Returns:
            PIL Image with side-by-side comparison and overlay
        """
        height, width = matrix_a.shape
        
        # Create side-by-side comparison
        img_width = width * self.module_size * 2 + 20  # 2 images + gap
        img_height = height * self.module_size + 100  # Image + stats area
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw original (left)
        self._draw_matrix(img, matrix_a, 0, 0, 'Original (A)')
        
        # Draw target (right)
        self._draw_matrix(img, matrix_b, width * self.module_size + 20, 0, 'Target (B)')
        
        # Draw overlay with flips (on original)
        if show_flips and flip_positions:
            overlay = self._create_flip_overlay(matrix_a, flip_positions)
            img.paste(overlay, (0, 0), overlay)
        
        # Add statistics text
        stats_text = f"Flips needed: {len(flip_positions)}"
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, height * self.module_size + 10), stats_text, fill='black', font=font)
        
        return img
    
    def _draw_matrix(self, img: Image.Image, matrix: np.ndarray, 
                    offset_x: int, offset_y: int, label: str, highlight_changes: bool = False):
        """Draw QR matrix on image with precise pixel alignment.
        
        Args:
            img: Image to draw on
            matrix: Matrix to draw (0=white, 1=black, 2=red highlight if highlight_changes=True)
            offset_x: X offset (exact pixel position)
            offset_y: Y offset (exact pixel position)
            label: Label text
            highlight_changes: If True, value 2 will be drawn as red
        """
        self._draw_matrix_no_label(img, matrix, offset_x, offset_y, highlight_changes)
        
        # Add label above the matrix (only if label provided)
        if label:
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font = ImageFont.load_default()
            draw.text((offset_x, offset_y - 20), label, fill='black', font=font)
    
    def _draw_matrix_no_label(self, img: Image.Image, matrix: np.ndarray, 
                             offset_x: int, offset_y: int, highlight_changes: bool = False,
                             original_matrix: Optional[np.ndarray] = None):
        """Draw QR matrix on image with precise pixel alignment (no label).
        
        Args:
            img: Image to draw on
            matrix: Matrix to draw (0=white, 1=black, 2=red, 3=green if highlight_changes=True)
            offset_x: X offset (exact pixel position, integer)
            offset_y: Y offset (exact pixel position, integer)
            highlight_changes: If True, value 2=red (black→white), 3=green (white→black)
            original_matrix: Original matrix to show as base when highlighting
        """
        draw = ImageDraw.Draw(img)
        height, width = matrix.shape
        
        # Ensure integer offsets to prevent floating point issues
        offset_x = int(offset_x)
        offset_y = int(offset_y)
        
        # Draw each module with exact pixel positioning (no rounding)
        for y in range(height):
            for x in range(width):
                value = matrix[y, x]
                
                # Calculate exact pixel positions - ensure integer arithmetic
                x1 = offset_x + x * self.module_size
                y1 = offset_y + y * self.module_size
                x2 = x1 + self.module_size
                y2 = y1 + self.module_size
                
                if highlight_changes and original_matrix is not None:
                    # Show original matrix with colored highlights
                    original_val = original_matrix[y, x] if y < original_matrix.shape[0] and x < original_matrix.shape[1] else 0
                    
                    # Draw base (original)
                    if original_val == 1:
                        base_color = (0, 0, 0)  # Black
                    else:
                        base_color = (255, 255, 255)  # White
                    
                    draw.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=base_color, outline=None)
                    
                    # Overlay highlight if changed
                    if value == 3:
                        # Green highlight for white→black changes (semi-transparent overlay)
                        overlay = Image.new('RGBA', (self.module_size, self.module_size), (0, 255, 0, 180))
                        img.paste(overlay, (x1, y1), overlay)
                    elif value == 2:
                        # Red highlight for black→white changes (semi-transparent overlay)
                        overlay = Image.new('RGBA', (self.module_size, self.module_size), (255, 0, 0, 180))
                        img.paste(overlay, (x1, y1), overlay)
                elif highlight_changes:
                    # Fallback if no original_matrix provided
                    if value == 3:
                        color = (0, 255, 0)  # Green
                    elif value == 2:
                        color = (255, 0, 0)  # Red
                    elif value == 1:
                        color = (0, 0, 0)  # Black
                    else:
                        color = (255, 255, 255)  # White
                    draw.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=color, outline=None)
                elif value == 1:
                    # Black module
                    draw.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=(0, 0, 0), outline=None)
                else:
                    # White module
                    draw.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=(255, 255, 255), outline=None)
    
    def create_individual_qr_image(self, matrix: np.ndarray, label: str = "", 
                                   highlight_positions: List[Tuple[int, int]] = None,
                                   original_matrix: Optional[np.ndarray] = None) -> Image.Image:
        """Create a single QR code image.
        
        Args:
            matrix: QR code matrix (0=white, 1=black)
            label: Optional label text
            highlight_positions: Optional list of (row, col) positions to highlight
            original_matrix: Original matrix to compare for change direction (green/red)
        
        Returns:
            PIL Image with the QR code
        """
        height, width = matrix.shape
        label_height = 30 if label else 0
        padding = 10
        
        img_width = width * self.module_size + padding * 2
        img_height = height * self.module_size + padding * 2 + label_height
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw QR code
        qr_x = padding
        qr_y = padding + label_height
        
        for y in range(height):
            for x in range(width):
                x1 = qr_x + x * self.module_size
                y1 = qr_y + y * self.module_size
                x2 = x1 + self.module_size
                y2 = y1 + self.module_size
                
                # Check if this position should be highlighted
                is_highlight = highlight_positions and (y, x) in highlight_positions
                
                # Draw base: use original_matrix if provided (for diff visualization), otherwise use matrix
                if original_matrix is not None and 0 <= y < original_matrix.shape[0] and 0 <= x < original_matrix.shape[1]:
                    base_val = original_matrix[y, x]
                    new_val = matrix[y, x] if y < matrix.shape[0] and x < matrix.shape[1] else base_val
                else:
                    base_val = matrix[y, x]
                    new_val = base_val
                
                # Draw base color
                if base_val == 1:
                    base_color = (0, 0, 0)  # Black
                else:
                    base_color = (255, 255, 255)  # White
                
                draw.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=base_color, outline=None)
                
                # Overlay highlight if this position changed
                if is_highlight and original_matrix is not None:
                    if 0 <= y < original_matrix.shape[0] and 0 <= x < original_matrix.shape[1]:
                        original_val = original_matrix[y, x]
                        new_val = matrix[y, x] if y < matrix.shape[0] and x < matrix.shape[1] else original_val
                        if original_val == 0 and new_val == 1:
                            # Green overlay for white→black
                            overlay = Image.new('RGBA', (self.module_size, self.module_size), (0, 255, 0, 180))
                            img.paste(overlay, (x1, y1), overlay)
                        elif original_val == 1 and new_val == 0:
                            # Red overlay for black→white
                            overlay = Image.new('RGBA', (self.module_size, self.module_size), (255, 0, 0, 180))
                            img.paste(overlay, (x1, y1), overlay)
                elif is_highlight:
                    # Fallback: red overlay
                    overlay = Image.new('RGBA', (self.module_size, self.module_size), (255, 0, 0, 180))
                    img.paste(overlay, (x1, y1), overlay)
        
        # Add label if provided
        if label:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                font = ImageFont.load_default()
            draw.text((padding, padding), label, fill='black', font=font)
        
        return img
    
    def _create_flip_overlay(self, matrix: np.ndarray, 
                            flip_positions: List[Tuple[int, int]]) -> Image.Image:
        """Create overlay highlighting positions that need to flip."""
        height, width = matrix.shape
        overlay = Image.new('RGBA', (width * self.module_size, height * self.module_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        for row, col in flip_positions:
            if 0 <= row < height and 0 <= col < width:
                x1 = col * self.module_size
                y1 = row * self.module_size
                x2 = x1 + self.module_size
                y2 = y1 + self.module_size
                
                # Draw red highlight with transparency
                draw.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=(255, 0, 0, 128))
        
        return overlay
    
    def create_comparison_grid(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                              transformed: np.ndarray, flip_positions: List[Tuple[int, int]]) -> Image.Image:
        """Create a 2x2 grid showing: original, target, transformed, diff.
        
        Note: Labels are NOT included as they're handled in HTML.
        """
        # Ensure all matrices have the same dimensions for proper alignment
        max_height = max(matrix_a.shape[0], matrix_b.shape[0], 
                        transformed.shape[0] if transformed is not None else 0)
        max_width = max(matrix_a.shape[1], matrix_b.shape[1],
                       transformed.shape[1] if transformed is not None else 0)
        
        # Pad or crop all matrices to same size
        def align_matrix(matrix, target_h, target_w):
            h, w = matrix.shape
            # Create aligned matrix (pad with white/0)
            aligned = np.zeros((target_h, target_w), dtype=matrix.dtype)
            # Copy original into aligned (centered if needed)
            copy_h = min(h, target_h)
            copy_w = min(w, target_w)
            aligned[:copy_h, :copy_w] = matrix[:copy_h, :copy_w]
            return aligned
        
        matrix_a_aligned = align_matrix(matrix_a, max_height, max_width)
        matrix_b_aligned = align_matrix(matrix_b, max_height, max_width)
        
        if transformed is not None:
            transformed_aligned = align_matrix(transformed, max_height, max_width)
        else:
            transformed_aligned = matrix_a_aligned.copy()
        
        height, width = max_height, max_width
        gap = 20
        
        # Calculate QR code dimensions in pixels (exact, no rounding)
        qr_width_px = width * self.module_size
        qr_height_px = height * self.module_size
        
        # Calculate total image dimensions with consistent spacing (no labels)
        img_width = qr_width_px * 2 + gap * 3
        img_height = qr_height_px * 2 + gap * 3
        
        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Calculate exact positions for perfect alignment (pixel-perfect)
        # Top row Y position (no label offset)
        top_y = gap
        # Left column X position
        left_x = gap
        # Right column X position (left + QR width + gap) - exact calculation
        right_x = left_x + qr_width_px + gap
        
        # Top row: Original and Target (perfectly aligned, no labels)
        self._draw_matrix_no_label(img, matrix_a_aligned, left_x, top_y)
        self._draw_matrix_no_label(img, matrix_b_aligned, right_x, top_y)
        
        # Bottom row: Transformed and Diff (perfectly aligned with top row)
        bottom_y = top_y + qr_height_px + gap
        self._draw_matrix_no_label(img, transformed_aligned, left_x, bottom_y)
        
        # Diff visualization - filter flip positions to valid aligned coordinates
        valid_flip_positions = [(r, c) for r, c in flip_positions 
                               if 0 <= r < max_height and 0 <= c < max_width]
        diff_matrix = self._create_diff_matrix(matrix_a_aligned, transformed_aligned, valid_flip_positions)
        self._draw_matrix_no_label(img, diff_matrix, right_x, bottom_y, highlight_changes=True, original_matrix=matrix_a_aligned)
        
        return img
    
    def create_comparison_grid_svg(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                                   transformed: np.ndarray, flip_positions: List[Tuple[int, int]]) -> str:
        """Create a 2x2 grid as SVG showing: original, target, transformed, diff.
        
        Returns SVG string for high-quality rendering.
        """
        # Ensure all matrices have the same dimensions
        max_height = max(matrix_a.shape[0], matrix_b.shape[0], 
                        transformed.shape[0] if transformed is not None else 0)
        max_width = max(matrix_a.shape[1], matrix_b.shape[1],
                       transformed.shape[1] if transformed is not None else 0)
        
        def align_matrix(matrix, target_h, target_w):
            h, w = matrix.shape
            aligned = np.zeros((target_h, target_w), dtype=matrix.dtype)
            copy_h = min(h, target_h)
            copy_w = min(w, target_w)
            aligned[:copy_h, :copy_w] = matrix[:copy_h, :copy_w]
            return aligned
        
        matrix_a_aligned = align_matrix(matrix_a, max_height, max_width)
        matrix_b_aligned = align_matrix(matrix_b, max_height, max_width)
        
        if transformed is not None:
            transformed_aligned = align_matrix(transformed, max_height, max_width)
        else:
            transformed_aligned = matrix_a_aligned.copy()
        
        height, width = max_height, max_width
        gap = 20
        qr_width_px = width * self.module_size
        qr_height_px = height * self.module_size
        img_width = qr_width_px * 2 + gap * 3
        img_height = qr_height_px * 2 + gap * 3
        
        # Build SVG
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{img_width}" height="{img_height}">',
            '<rect width="100%" height="100%" fill="white"/>'
        ]
        
        # Helper to draw matrix as SVG
        def draw_matrix_svg(matrix, x_offset, y_offset):
            svg = []
            for y in range(height):
                for x in range(width):
                    value = matrix[y, x]
                    if value == 1:
                        color = "black"
                    else:
                        color = "white"
                    x1 = x_offset + x * self.module_size
                    y1 = y_offset + y * self.module_size
                    svg.append(f'<rect x="{x1}" y="{y1}" width="{self.module_size}" height="{self.module_size}" fill="{color}"/>')
            return svg
        
        # Top row
        top_y = gap
        left_x = gap
        right_x = left_x + qr_width_px + gap
        svg_parts.extend(draw_matrix_svg(matrix_a_aligned, left_x, top_y))
        svg_parts.extend(draw_matrix_svg(matrix_b_aligned, right_x, top_y))
        
        # Bottom row - Transformed (fix: use transformed_aligned, not matrix_a)
        bottom_y = top_y + qr_height_px + gap
        svg_parts.extend(draw_matrix_svg(transformed_aligned, left_x, bottom_y))
        
        # Diff with highlights (green for white→black, red for black→white)
        valid_flip_positions = [(r, c) for r, c in flip_positions 
                               if 0 <= r < max_height and 0 <= c < max_width]
        diff_matrix = self._create_diff_matrix(matrix_a_aligned, transformed_aligned, valid_flip_positions)
        
        # Draw diff matrix: show original with colored highlights
        for y in range(height):
            for x in range(width):
                diff_value = diff_matrix[y, x]
                original_value = matrix_a_aligned[y, x]
                x1 = right_x + x * self.module_size
                y1 = bottom_y + y * self.module_size
                
                # Draw base (original matrix)
                if original_value == 1:
                    base_color = "black"
                else:
                    base_color = "white"
                
                # Overlay highlight if this position changed
                if diff_value == 3:
                    # Green highlight for white→black changes
                    svg_parts.append(f'<rect x="{x1}" y="{y1}" width="{self.module_size}" height="{self.module_size}" fill="{base_color}"/>')
                    svg_parts.append(f'<rect x="{x1}" y="{y1}" width="{self.module_size}" height="{self.module_size}" fill="green" opacity="0.7"/>')
                elif diff_value == 2:
                    # Red highlight for black→white changes
                    svg_parts.append(f'<rect x="{x1}" y="{y1}" width="{self.module_size}" height="{self.module_size}" fill="{base_color}"/>')
                    svg_parts.append(f'<rect x="{x1}" y="{y1}" width="{self.module_size}" height="{self.module_size}" fill="red" opacity="0.7"/>')
                else:
                    # No change - just draw base
                    svg_parts.append(f'<rect x="{x1}" y="{y1}" width="{self.module_size}" height="{self.module_size}" fill="{base_color}"/>')
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    def _create_diff_matrix(self, original: np.ndarray, transformed: np.ndarray,
                           flip_positions: List[Tuple[int, int]]) -> np.ndarray:
        """Create matrix highlighting differences with direction.
        
        Returns a matrix where:
        - 0 = white (no change)
        - 1 = black (no change)  
        - 2 = red highlight (black→white change)
        - 3 = green highlight (white→black change)
        """
        diff = original.copy().astype(np.uint8)
        # Mark changed positions with direction
        for row, col in flip_positions:
            if 0 <= row < diff.shape[0] and 0 <= col < diff.shape[1]:
                original_val = original[row, col]
                transformed_val = transformed[row, col] if row < transformed.shape[0] and col < transformed.shape[1] else original_val
                
                # Determine change direction
                if original_val == 0 and transformed_val == 1:
                    # White→Black: Green
                    diff[row, col] = 3
                elif original_val == 1 and transformed_val == 0:
                    # Black→White: Red
                    diff[row, col] = 2
                else:
                    # Fallback: use red
                    diff[row, col] = 2
        return diff
    
    def generate_heatmap(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                        flip_positions: List[Tuple[int, int]], format: str = 'svg') -> Union[Image.Image, str]:
        """Generate heatmap showing transformation intensity.
        
        Args:
            matrix_a: Original matrix
            matrix_b: Target matrix
            flip_positions: List of positions that changed
            format: Output format ('svg' or 'png')
        
        Returns:
            PIL Image (or SVG string if format='svg')
        """
        height, width = matrix_a.shape
        
        # Create heatmap: 0 = no change, 1 = change
        heatmap = np.zeros((height, width))
        for row, col in flip_positions:
            if 0 <= row < height and 0 <= col < width:
                heatmap[row, col] = 1
        
        # Use matplotlib for heatmap with fixed positioning
        fig, ax = plt.subplots(figsize=(width/10, height/10))
        # Use extent to ensure pixel-perfect alignment
        im = ax.imshow(heatmap, cmap='Reds', interpolation='nearest', vmin=0, vmax=1,
                      extent=[0, width, height, 0], aspect='equal')
        ax.set_title('Transformation Heatmap (Red = Module Flip)')
        ax.axis('off')
        
        # Remove padding/margins that cause shifts
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        
        # Convert to PIL Image or SVG
        buf = BytesIO()
        if format.lower() == 'svg':
            plt.savefig(buf, format='svg', bbox_inches='tight', pad_inches=0, dpi=100)
            buf.seek(0)
            svg_content = buf.read().decode('utf-8')
            plt.close()
            return svg_content
        else:
            plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=100)
            buf.seek(0)
            img = Image.open(buf)
            plt.close()
            return img
    
    def create_animation_frames(self, matrix_a: np.ndarray, matrix_b: np.ndarray,
                               flip_positions: List[Tuple[int, int]],
                               num_frames: int = 10) -> List[Image.Image]:
        """Create animation frames showing progressive transformation."""
        frames = []
        current_matrix = matrix_a.copy()
        
        # Sort flips for animation (could be randomized or ordered)
        flips_per_frame = max(1, len(flip_positions) // num_frames)
        
        for i in range(num_frames):
            start_idx = i * flips_per_frame
            end_idx = min((i + 1) * flips_per_frame, len(flip_positions))
            
            # Apply flips up to this frame
            for idx in range(start_idx, end_idx):
                row, col = flip_positions[idx]
                if 0 <= row < current_matrix.shape[0] and 0 <= col < current_matrix.shape[1]:
                    current_matrix[row, col] = 1 - current_matrix[row, col]
            
            # Create frame
            frame = self.visualize_transformation(
                matrix_a, matrix_b, flip_positions[:end_idx], show_flips=True
            )
            frames.append(frame)
        
        return frames
