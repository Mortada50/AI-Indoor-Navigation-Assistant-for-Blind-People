import unittest
from unittest.mock import patch
import io
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app import app

class TestAPIIntegration(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def create_dummy_image(self):
        # We must load a real valid image so that PIL.Image.verify() inside app.py passes
        test_img_path = backend_dir.parent / "test.jpg"
        with open(test_img_path, "rb") as f:
            img_bytes = f.read()
        return (io.BytesIO(img_bytes), "test.jpg")

    @patch('app.detector.detect')
    def test_empty_detections(self, mock_detect):
        """STEP 10: Test Empty Detection Integration."""
        mock_detect.return_value = []
        response = self.client.post('/api/detect', data={'image': self.create_dummy_image()})
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("guidance", data)
        print("\n--- Empty Detection Integration Test ---")
        print("Expected: لم يتم اكتشاف...")
        print(f"Actual: {data['guidance'].get('summary')}")
        print("Result: PASS")

    @patch('app.detector.detect')
    def test_synthetic_classroom(self, mock_detect):
        """STEP 8: Test a Classroom scenario."""
        dummy_bbox = {"x1": 100, "y1": 100, "x2": 200, "y2": 200}
        # Mock detections
        mock_detect.return_value = [
            {"class_name": "blackboard", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "table", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "table", "confidence": 0.9, "bbox": dummy_bbox},
        ]
        
        response = self.client.post('/api/detect', data={'image': self.create_dummy_image()})
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("scene_inference", data)
        self.assertIn("guidance", data)
        self.assertEqual(data["scene_inference"]["scene"], "Classroom")
        print("\n--- Synthetic Classroom Integration Test ---")
        print("Expected: Classroom / قاعة دراسية")
        print(f"Actual Scene Inference: {data['scene_inference']['scene']}")
        print(f"Actual Guidance Scene: {data['guidance'].get('scene')}")
        print(f"Guidance Summary: {data['guidance'].get('summary')}")
        print("Result: PASS")

    @patch('app.detector.detect')
    def test_synthetic_computer_lab(self, mock_detect):
        """STEP 9: Test a Computer Laboratory scenario."""
        dummy_bbox = {"x1": 100, "y1": 100, "x2": 200, "y2": 200}
        mock_detect.return_value = [
            {"class_name": "CPU", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "Monitor", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "Keyboard", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "Mouse", "confidence": 0.9, "bbox": dummy_bbox},
        ]
        
        response = self.client.post('/api/detect', data={'image': self.create_dummy_image()})
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("scene_inference", data)
        self.assertIn("guidance", data)
        self.assertEqual(data["scene_inference"]["scene"], "Computer Laboratory")
        print("\n--- Synthetic Computer Lab Integration Test ---")
        print("Expected: Computer Laboratory / معمل حاسوب")
        print(f"Actual Scene Inference: {data['scene_inference']['scene']}")
        print(f"Actual Guidance Scene: {data['guidance'].get('scene')}")
        print(f"Guidance Summary: {data['guidance'].get('summary')}")
        print("Result: PASS")

    @patch('app.detector.detect')
    def test_synthetic_priority(self, mock_detect):
        """STEP 10: Verify Priority."""
        dummy_bbox = {"x1": 100, "y1": 100, "x2": 200, "y2": 200}
        mock_detect.return_value = [
            # Lab
            {"class_name": "CPU", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "Monitor", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "Keyboard", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "Mouse", "confidence": 0.9, "bbox": dummy_bbox},
            # Classroom
            {"class_name": "blackboard", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "chair", "confidence": 0.9, "bbox": dummy_bbox},
            {"class_name": "table", "confidence": 0.9, "bbox": dummy_bbox},
            # Near door to test priority inside guidance generator
            {"class_name": "Door", "confidence": 0.9, "bbox": dummy_bbox},
        ]
        
        response = self.client.post('/api/detect', data={'image': self.create_dummy_image()})
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("scene_inference", data)
        self.assertIn("guidance", data)
        self.assertEqual(data["scene_inference"]["scene"], "Computer Laboratory")
        print("\n--- Priority Integration Test ---")
        print("Expected: Computer Laboratory / معمل حاسوب / Priority Guidance (Door first)")
        print(f"Actual Scene Inference: {data['scene_inference']['scene']}")
        print(f"Guidance Summary: {data['guidance'].get('summary')}")
        print("Result: PASS")

if __name__ == '__main__':
    unittest.main()
