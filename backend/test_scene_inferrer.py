import unittest
import sys
import json
from pathlib import Path
from PIL import Image

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from modules.scene_inferrer import SceneInferrer

class TestSceneInferrer(unittest.TestCase):
    
    def setUp(self):
        self.inferrer = SceneInferrer(conf_threshold=0.25)

    def test_1_classroom(self):
        """TEST 1 - CLASSROOM"""
        detections = [
            {"class_name": "blackboard", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "table", "confidence": 0.90},
            {"class_name": "table", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Classroom")
        self.assertEqual(result["object_counts"]["blackboard"], 1)
        self.assertEqual(result["object_counts"]["chair"], 5)
        self.assertEqual(result["object_counts"]["table"], 2)

    def test_2_computer_laboratory(self):
        """TEST 2 - COMPUTER LABORATORY"""
        detections = [
            {"class_name": "CPU", "confidence": 0.90},
            {"class_name": "Monitor", "confidence": 0.90},
            {"class_name": "Keyboard", "confidence": 0.90},
            {"class_name": "Mouse", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Computer Laboratory")

    def test_3_unknown(self):
        """TEST 3 - UNKNOWN"""
        detections = [
            {"class_name": "Door", "confidence": 0.90},
            {"class_name": "window", "confidence": 0.90},
            {"class_name": "window", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Unknown Indoor Space")

    def test_4_empty_detections(self):
        """TEST 4 - EMPTY DETECTIONS"""
        result = self.inferrer.estimate_scene([])
        self.assertEqual(result["scene"], "Unknown Indoor Space")
        self.assertEqual(result["object_counts"], {})

    def test_5_insufficient_classroom(self):
        """TEST 5 - INSUFFICIENT CLASSROOM OBJECTS"""
        detections = [
            {"class_name": "blackboard", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "table", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Unknown Indoor Space")

    def test_6_incomplete_computer_lab(self):
        """TEST 6 - INCOMPLETE COMPUTER LAB"""
        detections = [
            {"class_name": "CPU", "confidence": 0.90},
            {"class_name": "Monitor", "confidence": 0.90},
            {"class_name": "Keyboard", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Unknown Indoor Space")

    def test_7_priority(self):
        """TEST 7 - PRIORITY"""
        detections = [
            {"class_name": "CPU", "confidence": 0.90},
            {"class_name": "Monitor", "confidence": 0.90},
            {"class_name": "Keyboard", "confidence": 0.90},
            {"class_name": "Mouse", "confidence": 0.90},
            {"class_name": "blackboard", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "table", "confidence": 0.90},
            {"class_name": "table", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Computer Laboratory")

    def test_8_low_confidence_filter(self):
        """TEST 8 - LOW CONFIDENCE FILTER"""
        detections = [
            {"class_name": "blackboard", "confidence": 0.10}, # Below threshold
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "chair", "confidence": 0.90},
            {"class_name": "table", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Unknown Indoor Space")
        # Ensure blackboard wasn't counted
        self.assertNotIn("blackboard", result["object_counts"])

    def test_9_case_normalization(self):
        """TEST 9 - CASE NORMALIZATION"""
        detections = [
            {"class_name": "CPU", "confidence": 0.90},
            {"class_name": "monitor", "confidence": 0.90},
            {"class_name": "KEYBOARD", "confidence": 0.90},
            {"class_name": "mouse", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Computer Laboratory")
        self.assertIn("cpu", result["object_counts"])
        self.assertIn("keyboard", result["object_counts"])

    def test_10_unknown_classes(self):
        """TEST 10 - UNKNOWN CLASSES"""
        detections = [
            {"class_name": "backpack", "confidence": 0.90},
            {"class_name": "person", "confidence": 0.90},
            {"class_name": "phone", "confidence": 0.90}
        ]
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Unknown Indoor Space")
        self.assertEqual(result["object_counts"]["backpack"], 1)

    def test_11_multiple_object_counts(self):
        """TEST 11 - MULTIPLE OBJECT COUNTS"""
        detections = [
            {"class_name": "blackboard", "confidence": 0.90},
            {"class_name": "blackboard", "confidence": 0.90},
        ]
        detections += [{"class_name": "chair", "confidence": 0.90} for _ in range(10)]
        detections += [{"class_name": "table", "confidence": 0.90} for _ in range(4)]
        
        result = self.inferrer.estimate_scene(detections)
        self.assertEqual(result["scene"], "Classroom")
        self.assertEqual(result["object_counts"]["blackboard"], 2)
        self.assertEqual(result["object_counts"]["chair"], 10)
        self.assertEqual(result["object_counts"]["table"], 4)


def test_real_yolo_integration():
    print("\n--- Real YOLO Integration Test ---")
    try:
        from modules.detector import YoloDetector
        detector = YoloDetector()
        
        test_image_path = backend_dir.parent / "test.jpg"
        print(f"Loading image from {test_image_path}")
        image = Image.open(test_image_path)
        
        raw_detections = detector.detect(image)
        print(f"Raw YOLO detections found: {len(raw_detections)}")
        
        inferrer = SceneInferrer()
        result = inferrer.estimate_scene(raw_detections)
        
        print("\nScene Inference Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Failed Real YOLO test: {e}")

if __name__ == '__main__':
    # Run unit tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSceneInferrer)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Run real integration test
    if test_result.wasSuccessful():
        test_real_yolo_integration()
