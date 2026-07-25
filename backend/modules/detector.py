import os
import sys
from pathlib import Path

# Try to import ultralytics, fail gracefully if not available yet (for future API)
try:
    from ultralytics import YOLO
except ImportError as e:
    YOLO = None
    IMPORT_ERROR = e

class YoloDetector:
    """
    Reusable YOLO11n object detector module.
    Loads the model once upon initialization.
    """
    
    def __init__(self, model_filename="best.pt"):
        """
        Initializes the detector and loads the model.
        
        Args:
            model_filename (str): The name of the model file inside backend/models.
        """
        if YOLO is None:
            raise RuntimeError(f"Failed to import ultralytics: {IMPORT_ERROR}")
            
        # Robust path resolution: resolve path relative to this file's location
        # This file is in backend/modules/detector.py
        # Model should be in backend/models/best.pt
        current_dir = Path(__file__).resolve().parent
        backend_dir = current_dir.parent
        self.model_path = backend_dir / "models" / model_filename
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {self.model_path}")
            
        try:
            # Load the YOLO model once
            self.model = YOLO(str(self.model_path))
            # Cache the dynamic class names from the loaded model
            self.class_names = self.model.names
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")

    def detect(self, image_input, conf_threshold=0.25, device="cpu"):
        """
        Runs YOLO inference on a single image.
        
        Args:
            image_input: Image path (str), NumPy array, or PIL image.
            conf_threshold (float): Minimum confidence threshold (default: 0.25).
            device (str): Inference device, e.g., "cpu" or "cuda" (default: "cpu").
            
        Returns:
            list: A list of dictionaries representing detected objects.
                  Format: [{'class_id': int, 'class_name': str, 'confidence': float, 'bbox': {'x1', 'y1', 'x2', 'y2'}}, ...]
        """
        if image_input is None:
            raise ValueError("Invalid image input provided (None).")
            
        try:
            # Run inference
            # We set verbose=False to reduce terminal spam, and pass the configurable conf/device
            results = self.model.predict(
                source=image_input,
                conf=conf_threshold,
                device=device,
                verbose=False,
                save=False
            )
            
            structured_results = []
            
            # Process results (Ultralytics returns a list of Results objects, usually 1 for a single image)
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                    
                for box in boxes:
                    # Extract values
                    cls_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())
                    # bbox in xyxy format: x1, y1, x2, y2
                    xyxy = box.xyxy[0].tolist()
                    
                    detection = {
                        "class_id": cls_id,
                        "class_name": self.class_names.get(cls_id, f"Unknown_{cls_id}"),
                        "confidence": confidence,
                        "bbox": {
                            "x1": round(xyxy[0], 2),
                            "y1": round(xyxy[1], 2),
                            "x2": round(xyxy[2], 2),
                            "y2": round(xyxy[3], 2)
                        }
                    }
                    structured_results.append(detection)
                    
            return structured_results
            
        except Exception as e:
            raise RuntimeError(f"YOLO inference failed: {e}")

