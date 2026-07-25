import unittest
import sys
import json
from pathlib import Path
from PIL import Image

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from modules.spatial_analyzer import SpatialAnalyzer

class TestSpatialAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.image_width = 1000

    def test_1_object_left(self):
        """Test 1: Object clearly on the left."""
        detections = [{"bbox": {"x1": 100, "y1": 50, "x2": 200, "y2": 150}}]
        result = SpatialAnalyzer.analyze_detections(detections, self.image_width)
        self.assertEqual(result[0]['spatial']['horizontal_position'], "left")
        self.assertAlmostEqual(result[0]['spatial']['normalized_x'], 0.15)

    def test_2_object_center(self):
        """Test 2: Object clearly in the center."""
        detections = [{"bbox": {"x1": 400, "y1": 50, "x2": 600, "y2": 150}}]
        result = SpatialAnalyzer.analyze_detections(detections, self.image_width)
        self.assertEqual(result[0]['spatial']['horizontal_position'], "center")
        self.assertAlmostEqual(result[0]['spatial']['normalized_x'], 0.5)

    def test_3_object_right(self):
        """Test 3: Object clearly on the right."""
        detections = [{"bbox": {"x1": 800, "y1": 50, "x2": 900, "y2": 150}}]
        result = SpatialAnalyzer.analyze_detections(detections, self.image_width)
        self.assertEqual(result[0]['spatial']['horizontal_position'], "right")
        self.assertAlmostEqual(result[0]['spatial']['normalized_x'], 0.85)

    def test_4_object_boundary(self):
        """Test 4: Object exactly at a boundary (0.33 and 0.66)."""
        # Center exactly at 330 -> norm_x = 0.33
        detections = [{"bbox": {"x1": 330, "y1": 50, "x2": 330, "y2": 150}}]
        result = SpatialAnalyzer.analyze_detections(detections, self.image_width)
        self.assertEqual(result[0]['spatial']['horizontal_position'], "center")
        
        # Center exactly at 660 -> norm_x = 0.66
        detections2 = [{"bbox": {"x1": 660, "y1": 50, "x2": 660, "y2": 150}}]
        result2 = SpatialAnalyzer.analyze_detections(detections2, self.image_width)
        self.assertEqual(result2[0]['spatial']['horizontal_position'], "right")

    def test_5_multiple_detections(self):
        """Test 5: Multiple detections."""
        detections = [
            {"class_name": "chair", "bbox": {"x1": 0, "y1": 0, "x2": 100, "y2": 100}}, # Left
            {"class_name": "laptop", "bbox": {"x1": 450, "y1": 0, "x2": 550, "y2": 100}}, # Center
            {"class_name": "chair", "bbox": {"x1": 900, "y1": 0, "x2": 1000, "y2": 100}}  # Right
        ]
        result = SpatialAnalyzer.analyze_detections(detections, self.image_width)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['spatial']['horizontal_position'], "left")
        self.assertEqual(result[1]['spatial']['horizontal_position'], "center")
        self.assertEqual(result[2]['spatial']['horizontal_position'], "right")

    def test_6_different_resolutions(self):
        """Test 6: Different image resolutions."""
        detections = [{"bbox": {"x1": 960, "y1": 0, "x2": 960, "y2": 100}}] # Center of 1920
        result = SpatialAnalyzer.analyze_detections(detections, 1920)
        self.assertEqual(result[0]['spatial']['horizontal_position'], "center")
        self.assertAlmostEqual(result[0]['spatial']['normalized_x'], 0.5)
        
        detections2 = [{"bbox": {"x1": 2016, "y1": 0, "x2": 2016, "y2": 100}}] # Center of 4032
        result2 = SpatialAnalyzer.analyze_detections(detections2, 4032)
        self.assertEqual(result2[0]['spatial']['horizontal_position'], "center")
        self.assertAlmostEqual(result2[0]['spatial']['normalized_x'], 0.5)

    def test_7_invalid_width(self):
        """Test 7: Invalid image width."""
        detections = [{"bbox": {"x1": 100, "y1": 50, "x2": 200, "y2": 150}}]
        with self.assertRaises(ValueError):
            SpatialAnalyzer.analyze_detections(detections, 0)
        with self.assertRaises(ValueError):
            SpatialAnalyzer.analyze_detections(detections, -100)
        with self.assertRaises(ValueError):
            SpatialAnalyzer.analyze_detections(detections, "not-a-number")

    def test_8_invalid_bbox(self):
        """Test 8: Invalid bounding box."""
        # Missing bbox
        with self.assertRaises(ValueError):
            SpatialAnalyzer.analyze_detections([{"class_name": "chair"}], 1000)
        # x1 > x2
        with self.assertRaises(ValueError):
            SpatialAnalyzer.analyze_detections([{"bbox": {"x1": 500, "y1": 50, "x2": 100, "y2": 150}}], 1000)
        # Missing x2
        with self.assertRaises(ValueError):
            SpatialAnalyzer.analyze_detections([{"bbox": {"x1": 100, "y1": 50, "y2": 150}}], 1000)

def test_real_yolo_integration():
    print("\n--- Real YOLO Integration Test ---")
    
    # We must run this test separately so it doesn't block unit tests if model loading fails
    try:
        from modules.detector import YoloDetector
        detector = YoloDetector()
        
        test_image_path = backend_dir.parent / "test.jpg"
        print(f"Loading image from {test_image_path}")
        image = Image.open(test_image_path)
        img_width, _ = image.size
        print(f"Image width: {img_width}")
        
        raw_detections = detector.detect(image)
        print(f"Raw YOLO detections found: {len(raw_detections)}")
        
        enriched_detections = SpatialAnalyzer.analyze_detections(raw_detections, img_width)
        
        print("\nEnriched Detections:")
        for det in enriched_detections:
            print(f"- Class: {det['class_name']}")
            print(f"  Bbox: {det['bbox']}")
            print(f"  Center X: {det['spatial']['center_x']}")
            print(f"  Normalized X: {det['spatial']['normalized_x']}")
            print(f"  Position: {det['spatial']['horizontal_position']}\n")
            
    except Exception as e:
        print(f"Failed Real YOLO test: {e}")

if __name__ == '__main__':
    # Run unit tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSpatialAnalyzer)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Run real integration test
    if test_result.wasSuccessful():
        test_real_yolo_integration()
