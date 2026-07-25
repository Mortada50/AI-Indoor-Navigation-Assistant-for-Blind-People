class SceneInferrer:
    """
    A reusable module for estimating the educational environment based on
    objects detected by YOLO11n using predefined rule-based logic.

    IMPORTANT: This is a deterministic rule-based heuristic system. It is NOT
    a machine-learning scene classifier and the YOLO model does not predict the scene.
    """

    def __init__(self, conf_threshold: float = 0.25):
        """
        Initializes the SceneInferrer with configurable thresholds.

        Args:
            conf_threshold (float): Minimum YOLO detection confidence required
                                    for an object to be counted in scene inference.
        """
        self.conf_threshold = conf_threshold

    def estimate_scene(self, detections: list) -> dict:
        """
        Estimates the scene based on object detection counts and predefined rules.

        Args:
            detections (list): List of YOLO detection dictionaries.

        Returns:
            dict: Structured scene inference data.
        """
        if not isinstance(detections, list):
            raise TypeError("detections must be a list of dictionaries.")

        # 1. Filter by confidence and count normalized classes
        object_counts = {}
        for det in detections:
            confidence = det.get('confidence', 0.0)
            if confidence < self.conf_threshold:
                continue
                
            class_name = det.get('class_name')
            if not class_name or not isinstance(class_name, str):
                continue
                
            # Normalize class name
            normalized_name = class_name.strip().lower()
            
            # Increment count
            object_counts[normalized_name] = object_counts.get(normalized_name, 0) + 1

        # 2. Evaluate Rules (In order of priority)
        # Priority 1: Computer Laboratory
        # Priority 2: Classroom
        # Priority 3: Unknown Indoor Space
        
        scene = "Unknown Indoor Space"
        rule_score = 0.0
        matched_rules = []

        # Rule: Computer Laboratory
        if (
            object_counts.get('cpu', 0) >= 1 and
            object_counts.get('monitor', 0) >= 1 and
            object_counts.get('keyboard', 0) >= 1 and
            object_counts.get('mouse', 0) >= 1
        ):
            scene = "Computer Laboratory"
            rule_score = 1.0
            matched_rules = ["computer_laboratory"]

        # Rule: Classroom (Only if higher priority rules haven't matched)
        elif (
            object_counts.get('blackboard', 0) >= 1 and
            object_counts.get('chair', 0) >= 3 and
            object_counts.get('table', 0) >= 1
        ):
            scene = "Classroom"
            rule_score = 1.0
            matched_rules = ["classroom"]

        # 3. Return structured data
        return {
            "scene": scene,
            "rule_score": rule_score,
            "matched_rules": matched_rules,
            "object_counts": object_counts
        }
