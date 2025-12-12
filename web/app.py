"""FastAPI web application for QR code transformation."""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sys
import os
from pathlib import Path
from PIL import Image
import io
import base64
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.transformer import QRTransformer
from src.visualizer import QRVisualizer
from src.insights import generate_insights

app = FastAPI(title="QR Code Transformation Tool")

# Setup templates and static files
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main page."""
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/transform")
async def transform_qr(
    message_a: str = Form(None),
    message_b: str = Form(...),
    file: UploadFile = File(None),
    use_exact: bool = Form(True),
    respect_ecc: bool = Form(True)
):
    """
    Transform QR code from message A to message B.
    
    Either provide message_a and message_b, or upload a QR image and provide message_b.
    """
    try:
        # ECC level is now automatically optimized - all 4 levels (L, M, Q, H) are tested
        transformer = QRTransformer(ecc_level='M')  # Default, but all levels will be tested automatically
        visualizer = QRVisualizer(module_size=10)
        
        if file and file.filename:
            # Transform from uploaded image
            contents = await file.read()
            img = Image.open(io.BytesIO(contents))
            
            # Save temporarily
            temp_path = f"/tmp/qr_input_{os.getpid()}.png"
            img.save(temp_path)
            
            result = transformer.transform_from_image(
                temp_path, message_b, use_exact=use_exact, respect_ecc=respect_ecc
            )
            
            # Clean up
            os.remove(temp_path)
            
            # Get original matrix from image
            from src.utils import image_to_matrix
            matrix_a = image_to_matrix(img)
        else:
            # Transform from messages
            if not message_a:
                raise HTTPException(status_code=400, detail="Either message_a or file must be provided")
            
            result = transformer.transform(
                message_a, message_b, use_exact=use_exact, respect_ecc=respect_ecc
            )
            
            # Get matrices from encoder
            qr_a = transformer.encoder.encode(message_a)
            matrix_a = qr_a.module_matrix
        
        # Get target matrix
        qr_b = transformer.encoder.encode(message_b)
        matrix_b = qr_b.module_matrix
        
        # Ensure same dimensions
        if matrix_a.shape != matrix_b.shape:
            min_h = min(matrix_a.shape[0], matrix_b.shape[0])
            min_w = min(matrix_a.shape[1], matrix_b.shape[1])
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
            if result.transformed_matrix is not None:
                result.transformed_matrix = result.transformed_matrix[:min_h, :min_w]
        
        # Ensure transformed matrix exists and has correct dimensions
        if result.transformed_matrix is None:
            # Fallback: create transformed matrix from matrix_a with flips
            result.transformed_matrix = matrix_a.copy()
            for row, col in result.flip_positions:
                if 0 <= row < result.transformed_matrix.shape[0] and 0 <= col < result.transformed_matrix.shape[1]:
                    result.transformed_matrix[row, col] = 1 - result.transformed_matrix[row, col]
        
        # Ensure transformed matrix matches matrix_a dimensions
        if result.transformed_matrix.shape != matrix_a.shape:
            min_h = min(result.transformed_matrix.shape[0], matrix_a.shape[0])
            min_w = min(result.transformed_matrix.shape[1], matrix_a.shape[1])
            result.transformed_matrix = result.transformed_matrix[:min_h, :min_w]
            matrix_a = matrix_a[:min_h, :min_w]
            matrix_b = matrix_b[:min_h, :min_w]
        
        # Generate individual QR code images
        # Align all matrices to same size first
        max_height = max(matrix_a.shape[0], matrix_b.shape[0], 
                        result.transformed_matrix.shape[0] if result.transformed_matrix is not None else 0)
        max_width = max(matrix_a.shape[1], matrix_b.shape[1],
                       result.transformed_matrix.shape[1] if result.transformed_matrix is not None else 0)
        
        def align_matrix(matrix, target_h, target_w):
            h, w = matrix.shape
            aligned = np.zeros((target_h, target_w), dtype=matrix.dtype)
            copy_h = min(h, target_h)
            copy_w = min(w, target_w)
            aligned[:copy_h, :copy_w] = matrix[:copy_h, :copy_w]
            return aligned
        
        matrix_a_aligned = align_matrix(matrix_a, max_height, max_width)
        matrix_b_aligned = align_matrix(matrix_b, max_height, max_width)
        if result.transformed_matrix is not None:
            transformed_aligned = align_matrix(result.transformed_matrix, max_height, max_width)
        else:
            transformed_aligned = matrix_a_aligned.copy()
        
        # Create individual images (no labels - labels are in HTML)
        original_img = visualizer.create_individual_qr_image(matrix_a_aligned, "")
        target_img = visualizer.create_individual_qr_image(matrix_b_aligned, "")
        transformed_img = visualizer.create_individual_qr_image(transformed_aligned, "")
        
        # Create diff image: show ORIGINAL matrix with colored highlights
        # Pass transformed as matrix and original as original_matrix so it can determine direction
        valid_flip_positions = [(r, c) for r, c in result.flip_positions 
                               if 0 <= r < max_height and 0 <= c < max_width]
        diff_img = visualizer.create_individual_qr_image(
            transformed_aligned, "", highlight_positions=valid_flip_positions, original_matrix=matrix_a_aligned
        )
        
        # Convert images to SVG base64 for better quality
        def image_to_svg_base64(img: Image.Image) -> str:
            """Convert PIL Image to SVG base64 string for high quality rendering."""
            # For high quality, we'll use PNG but can be enhanced to true SVG
            # Using high DPI for better quality
            buf = io.BytesIO()
            # Save as high-quality PNG (SVG would require vector conversion)
            img.save(buf, format='PNG', optimize=False)
            img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            return img_b64
        
        original_b64 = image_to_svg_base64(original_img)
        target_b64 = image_to_svg_base64(target_img)
        transformed_b64 = image_to_svg_base64(transformed_img)
        diff_b64 = image_to_svg_base64(diff_img)
        
        # Generate insights
        insights = generate_insights(result, transformer.encoder, matrix_a, matrix_b)
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_native(obj):
            """Convert numpy types to native Python types."""
            # Handle numpy integers (NumPy 2.0 compatible)
            if isinstance(obj, np.integer):
                return int(obj)
            # Handle numpy floats (NumPy 2.0 compatible - np.float_ removed)
            elif isinstance(obj, np.floating):
                return float(obj)
            # Handle numpy bools (NumPy 2.0 compatible - np.bool8 removed)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            # Handle numpy arrays
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            # Recursively handle containers
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_to_native(item) for item in obj)
            return obj
        
        # Convert flip positions (tuples with numpy int64)
        flip_positions_native = [(int(row), int(col)) for row, col in result.flip_positions]
        
        # Convert stats dict
        stats_native = convert_to_native(result.stats)
        
        # Convert insights dict
        insights_native = convert_to_native(insights)
        
        # Get algorithm info
        algorithm_name = getattr(result, 'algorithm', 'unknown')
        algorithm_results = getattr(result, 'algorithm_results', {})
        
        return JSONResponse({
            "success": bool(result.success),
            "min_flips": int(result.min_flips),
            "flip_positions": flip_positions_native,
            "within_ecc": bool(result.within_ecc),
            "stats": stats_native,
            "images": {
                "original": original_b64,
                "target": target_b64,
                "transformed": transformed_b64,
                "changes": diff_b64
            },
            "insights": insights_native,
            "message_a": str(result.message_a),
            "message_b": str(result.message_b),
            "algorithm": algorithm_name,
            "algorithm_results": convert_to_native(algorithm_results)
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", "8000"))
    workers = int(os.environ.get("WORKERS", "1"))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        workers=workers if workers > 1 else None  # Only use workers if > 1
    )

