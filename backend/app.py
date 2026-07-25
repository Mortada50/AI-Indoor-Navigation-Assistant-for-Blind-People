"""
AI Indoor Navigation Assistant for Blind and Visually Impaired Users
Backend API — Flask Server with YOLO Integration

Phase 1 — Task 1.2-C: Integrate YOLO Detector with Flask API
"""

import os
import io
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image, UnidentifiedImageError
from werkzeug.exceptions import RequestEntityTooLarge

# Import the reusable YOLO detector module
try:
    from modules.detector import YoloDetector
    from modules.spatial_analyzer import SpatialAnalyzer
    from modules.distance_estimator import DistanceEstimator
    from modules.scene_inferrer import SceneInferrer
    from modules.guidance_generator import GuidanceGenerator
    
    print("Initializing modules...")
    detector = YoloDetector()
    spatial_analyzer = SpatialAnalyzer()
    distance_estimator = DistanceEstimator()
    scene_inferrer = SceneInferrer()
    guidance_generator = GuidanceGenerator()
    print("Modules initialized successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize modules: {e}")
    detector = None
    spatial_analyzer = None
    distance_estimator = None
    scene_inferrer = None
    guidance_generator = None

# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Enable Cross-Origin Resource Sharing dynamically for Production
cors_origins = os.environ.get("CORS_ORIGINS", "*")
if cors_origins != "*":
    # Support multiple origins separated by commas
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]
CORS(app, origins=cors_origins)

# Configure Maximum Upload Size (10 MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_exceeded(e):
    """Handles oversized uploads gracefully."""
    return jsonify({
        "success": False,
        "error": "File size exceeds the 10 MB limit."
    }), 413


# ---------------------------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({
        "success": True,
        "status": "ok",
        "service": "AI Indoor Navigation Assistant API"
    }), 200


# ---------------------------------------------------------------------------
# Object Detection Endpoint
# ---------------------------------------------------------------------------

@app.route("/api/detect", methods=["POST"])
def detect():
    """
    Detect objects in an uploaded image using the YOLO model.

    Expects:
        Content-Type: multipart/form-data
        Field: 'image' (image file)

    Returns:
        JSON: { success, detections: [...] } or { success, error }
    """
    if detector is None:
        return jsonify({"success": False, "error": "Detector module is not initialized server-side."}), 500

    # 1. Validate image field
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "Image file is required"}), 400
        
    file = request.files['image']

    # 2. Validate filename
    if file.filename == '':
        return jsonify({"success": False, "error": "Empty filename"}), 400

    # 3. Read and Decode Image
    try:
        # Read the file directly into memory without saving to disk
        image_bytes = file.read()
        # Decode the image using PIL to ensure it's a valid image
        image = Image.open(io.BytesIO(image_bytes))
        image.verify() # verifies it's an image without fully decoding
        
        # We need to reopen because verify() messes up the file pointer for inference
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB in case of RGBA/P formats to avoid inference issues
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
    except UnidentifiedImageError:
        return jsonify({"success": False, "error": "Invalid or unsupported image format."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "Corrupted or unreadable image file."}), 400

    # 4. YOLO Inference, Spatial Analysis, Distance Estimation, and Scene Inference
    try:
        # Use default conf=0.25 and device="cpu" defined in the detector module
        raw_detections = detector.detect(image_input=image)
        
        # Estimate scene based purely on raw YOLO detections
        scene_inference = scene_inferrer.estimate_scene(raw_detections)
        
        # Determine actual image width and height
        image_width, image_height = image.size
        
        # Enrich detections with horizontal spatial position
        spatial_detections = spatial_analyzer.analyze_detections(
            detections=raw_detections, 
            image_width=image_width
        )

        # Enrich detections with relative proximity
        enriched_detections = distance_estimator.estimate_proximity(
            detections=spatial_detections,
            image_width=image_width,
            image_height=image_height
        )
        
        # Generate natural Arabic guidance based on final enriched detections
        guidance = guidance_generator.generate(
            detections=enriched_detections, 
            scene_inference=scene_inference
        )
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal inference failure: {e}"}), 500

    # 5. Return JSON Response
    response = jsonify({
        "success": True,
        "scene_inference": scene_inference,
        "guidance": guidance,
        "detections": enriched_detections
    })
    
    # 6. Manual Garbage Collection to prevent Render 512MB OOM
    import gc
    gc.collect()
    
    return response, 200


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )
