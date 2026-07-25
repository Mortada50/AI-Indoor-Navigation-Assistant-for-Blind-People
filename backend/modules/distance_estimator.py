import copy

class DistanceEstimator:
    """
    A reusable module for relative proximity estimation of object detections.
    
    IMPORTANT LIMITATION:
    1. This is a RELATIVE PROXIMITY estimation module.
    2. It is based solely on bounding box size (normalized area).
    3. It is NOT a true physical distance measurement (e.g., in meters).
    4. Results depend heavily on object size, camera perspective, object orientation,
       camera position, and bounding box accuracy.
    5. The thresholds are MVP heuristics and require real-world calibration.
    """

    def __init__(self, near_threshold: float = 0.40, medium_threshold: float = 0.10):
        """
        Initializes the DistanceEstimator with configurable thresholds.

        Args:
            near_threshold (float): Normalized area >= this value is considered "near".
            medium_threshold (float): Normalized area >= this value (and < near) is "medium".
                                      Values below medium_threshold are "far".
        """
        self.near_threshold = near_threshold
        self.medium_threshold = medium_threshold

    def estimate_proximity(self, detections: list, image_width: float, image_height: float) -> list:
        """
        Analyzes a list of detection dictionaries and appends relative proximity information.

        Args:
            detections (list): List of detection dicts containing at least 'bbox' {'x1', 'y1', 'x2', 'y2'}.
            image_width (float): The width of the original image used for inference.
            image_height (float): The height of the original image used for inference.

        Returns:
            list: A new list of detection dicts with an added 'distance' key.
        """
        if not isinstance(image_width, (int, float)) or image_width <= 0:
            raise ValueError(f"Invalid image_width: {image_width}. Must be a positive number.")
        
        if not isinstance(image_height, (int, float)) or image_height <= 0:
            raise ValueError(f"Invalid image_height: {image_height}. Must be a positive number.")

        if not isinstance(detections, list):
            raise TypeError("detections must be a list of dictionaries.")

        enriched_detections = []
        image_area = float(image_width * image_height)

        for det in detections:
            enriched = copy.deepcopy(det)
            
            bbox = enriched.get('bbox')
            if not bbox or not isinstance(bbox, dict):
                raise ValueError(f"Detection is missing a valid 'bbox' dictionary: {det}")

            try:
                # Safely parse floats
                x1 = float(bbox['x1'])
                y1 = float(bbox['y1'])
                x2 = float(bbox['x2'])
                y2 = float(bbox['y2'])
            except (KeyError, ValueError, TypeError):
                raise ValueError(f"Bounding box must contain numeric 'x1', 'y1', 'x2', 'y2' keys. Found: {bbox}")

            if x1 > x2:
                raise ValueError(f"Invalid bounding box: x1 ({x1}) cannot be greater than x2 ({x2}).")
            if y1 > y2:
                raise ValueError(f"Invalid bounding box: y1 ({y1}) cannot be greater than y2 ({y2}).")

            # Clamp bounding boxes to image dimensions to handle out-of-bound boxes
            x1 = max(0.0, min(x1, float(image_width)))
            x2 = max(0.0, min(x2, float(image_width)))
            y1 = max(0.0, min(y1, float(image_height)))
            y2 = max(0.0, min(y2, float(image_height)))

            # Calculate width, height, and area
            bbox_width = x2 - x1
            bbox_height = y2 - y1
            bbox_area = bbox_width * bbox_height

            # Handle zero-area bbox gracefully
            if bbox_area == 0:
                normalized_area = 0.0
                area_ratio_percent = 0.0
                proximity = "far"  # Defaults to far if it has no area
            else:
                normalized_area = bbox_area / image_area
                # Clamp normalized_area in case of floating point inaccuracies
                normalized_area = max(0.0, min(1.0, normalized_area))
                area_ratio_percent = normalized_area * 100.0

                if normalized_area >= self.near_threshold:
                    proximity = "near"
                elif normalized_area >= self.medium_threshold:
                    proximity = "medium"
                else:
                    proximity = "far"

            enriched['distance'] = {
                "normalized_area": round(normalized_area, 4),
                "area_ratio_percent": round(area_ratio_percent, 2),
                "proximity": proximity
            }
            
            enriched_detections.append(enriched)

        return enriched_detections
