class GuidanceGenerator:
    """
    Generates natural Arabic text guidance based on structured YOLO detection
    results, scene context, spatial data, and relative proximity.
    
    This module strictly provides environmental awareness. It does NOT command
    the user to move or imply absolute physical distances in meters/centimeters.
    """

    # 1. Object Name Translation
    CLASS_MAP = {
        "cpu": "وحدة المعالجة المركزية",
        "door": "باب",
        "keyboard": "لوحة مفاتيح",
        "monitor": "شاشة",
        "mouse": "فأرة",
        "blackboard": "سبورة",
        "chair": "كرسي",
        "laptop": "حاسوب محمول",
        "stairs": "درج",
        "table": "طاولة",
        "window": "نافذة"
    }

    # 2. Direction Translation
    POSITION_MAP = {
        "left": "على اليسار",
        "center": "أمامك",
        "right": "على اليمين"
    }

    # 3. Proximity Translation
    PROXIMITY_MAP = {
        "near": "قريب",
        "medium": "متوسط القرب",
        "far": "بعيد نسبيًا"
    }

    # Scene Translation
    SCENE_MAP = {
        "classroom": "قاعة دراسية",
        "computer laboratory": "معمل حاسوب",
        "unknown indoor space": "بيئة داخلية غير محددة"
    }

    # Priority configuration for sorting detections
    PRIORITY_CLASSES = {"door": 1, "stairs": 2}

    def _translate_class(self, class_name: str) -> str:
        if not class_name:
            return ""
        norm_name = class_name.lower().strip()
        return self.CLASS_MAP.get(norm_name, class_name)

    def _format_count(self, count: int, arabic_name: str) -> str:
        """Helper to format Arabic counts basically."""
        if count == 1:
            return arabic_name
        elif count == 2:
            return f"{arabic_name}ان" if not arabic_name.endswith("ة") else f"{arabic_name[:-1]}تان"
        elif 3 <= count <= 10:
            return f"{count} {arabic_name}ات"  # Simple pluralization heuristic
        else:
            return f"{count} {arabic_name}"

    def generate(self, detections: list, scene_inference: dict = None) -> dict:
        """
        Generates natural Arabic guidance text.
        
        Args:
            detections (list): List of enriched YOLO detections (must contain spatial/distance).
            scene_inference (dict, optional): Scene inference context.
            
        Returns:
            dict: Structured guidance containing summary string and individual messages.
        """
        if not isinstance(detections, list):
            detections = []
            
        # 1. Filter and validate detections defensively
        valid_detections = []
        for det in detections:
            if not isinstance(det, dict):
                continue
                
            class_name = det.get("class_name")
            spatial = det.get("spatial", {})
            distance = det.get("distance", {})
            
            horizontal = spatial.get("horizontal_position")
            proximity = distance.get("proximity")
            
            # Require minimum safe metadata
            if not class_name or not horizontal or not proximity:
                continue
                
            valid_detections.append(det)

        messages = []
        summary_parts = []

        # 2. Scene Context Contextualization
        scene_name = None
        if scene_inference and isinstance(scene_inference, dict):
            raw_scene = scene_inference.get("scene", "").lower()
            if raw_scene and raw_scene != "unknown indoor space":
                scene_name = self.SCENE_MAP.get(raw_scene, raw_scene)
                summary_parts.append(f"أنت في {scene_name}.")

        if not valid_detections:
            msg = "لم يتم اكتشاف أجسام واضحة أمامك حاليًا."
            if not summary_parts:
                summary_parts.append(msg)
            return {
                "summary": " ".join(summary_parts).strip(),
                "messages": [],
                "scene": scene_name or "بيئة داخلية غير محددة"
            }

        # 3. Deduplication and Aggregation
        # We group identical objects that share the same horizontal position and proximity
        grouped_objects = {}
        for det in valid_detections:
            c_name = det["class_name"].lower().strip()
            h_pos = det["spatial"]["horizontal_position"]
            prox = det["distance"]["proximity"]
            
            key = (c_name, h_pos, prox)
            if key not in grouped_objects:
                grouped_objects[key] = {"count": 0, "original": det}
            grouped_objects[key]["count"] += 1

        # 4. Sorting / Priority Ordering
        # Priority: 1. Door, 2. Stairs, 3. Near, 4. Center, 5. Others
        def sort_key(item):
            key_tuple, data = item
            c_name, h_pos, prox = key_tuple
            
            p_score = self.PRIORITY_CLASSES.get(c_name, 99)
            prox_score = 1 if prox == "near" else (2 if prox == "medium" else 3)
            pos_score = 1 if h_pos == "center" else 2
            return (p_score, prox_score, pos_score)

        sorted_groups = sorted(grouped_objects.items(), key=sort_key)

        # 5. Sentence Generation
        for key_tuple, data in sorted_groups:
            c_name, h_pos, prox = key_tuple
            count = data["count"]
            
            ar_name = self._translate_class(c_name)
            if count > 1:
                # Naive generic plural phrasing for duplicate groups
                ar_name = f"{count} من {ar_name}"
                
            ar_pos = self.POSITION_MAP.get(h_pos, h_pos)
            ar_prox = self.PROXIMITY_MAP.get(prox, prox)
            
            # Grammar structuring
            if h_pos == "center":
                msg = f"يوجد {ar_name} {ar_pos}، وهو {ar_prox}."
            else:
                msg = f"يوجد {ar_name} {ar_prox} {ar_pos}."
                
            messages.append(msg)

        # 6. Build final summary string
        # To avoid extreme repetition, we can concatenate the messages.
        if len(messages) <= 3:
            summary_parts.append(" ".join(messages))
        else:
            # If there are many objects, summarize the first 2 highest priority, and count the rest.
            summary_parts.append(" ".join(messages[:2]))
            summary_parts.append(f"بالإضافة إلى {len(messages) - 2} عناصر أخرى في البيئة المحيطة.")

        return {
            "summary": " ".join(summary_parts).strip(),
            "messages": messages,
            "scene": scene_name or self.SCENE_MAP.get("unknown indoor space")
        }
