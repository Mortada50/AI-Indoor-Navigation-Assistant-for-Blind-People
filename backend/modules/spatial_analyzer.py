import copy

class SpatialAnalyzer:
    """
    A reusable module for spatial analysis of object detections.
    Determines the horizontal position (left, center, right) of objects based on their bounding boxes.
    """

    @staticmethod
    def analyze_detections(detections: list, image_width: float) -> list:
        """
        Analyzes a list of detection dictionaries and appends spatial information.

        Args:
            detections (list): List of detection dicts containing at least 'bbox' {'x1', 'y1', 'x2', 'y2'}.
            image_width (float): The width of the original image used for inference.

        Returns:
            list: A new list of detection dicts with an added 'spatial' key.
        """
        if not isinstance(image_width, (int, float)) or image_width <= 0:
            raise ValueError(f"Invalid image_width: {image_width}. Must be a positive number.")

        if not isinstance(detections, list):
            raise TypeError("detections must be a list of dictionaries.")

        enriched_detections = []
        for det in detections:
            # Create a deep copy to avoid mutating the original data
            enriched = copy.deepcopy(det)
            
            bbox = enriched.get('bbox')
            if not bbox or not isinstance(bbox, dict):
                raise ValueError(f"Detection is missing a valid 'bbox' dictionary: {det}")

            try:
                x1 = float(bbox['x1'])
                x2 = float(bbox['x2'])
            except (KeyError, ValueError, TypeError):
                raise ValueError(f"Bounding box must contain numeric 'x1' and 'x2' keys. Found: {bbox}")

            if x1 > x2:
                raise ValueError(f"Invalid bounding box: x1 ({x1}) cannot be greater than x2 ({x2}).")

            # Calculate center and normalize
            center_x = (x1 + x2) / 2.0
            normalized_x = center_x / image_width

            # Ensure normalized_x is clamped gracefully if bbox slightly exceeds image bounds
            normalized_x = max(0.0, min(1.0, normalized_x))

            # Determine position
            # [0.0 - 0.33) -> left
            # [0.33 - 0.66) -> center
            # [0.66 - 1.0] -> right
            if normalized_x < 0.33:
                horizontal_position = "left"
            elif normalized_x < 0.66:
                horizontal_position = "center"
            else:
                horizontal_position = "right"

            enriched['spatial'] = {
                "center_x": round(center_x, 2),
                "normalized_x": round(normalized_x, 3),
                "horizontal_position": horizontal_position
            }
            
            enriched_detections.append(enriched)

        return enriched_detections
