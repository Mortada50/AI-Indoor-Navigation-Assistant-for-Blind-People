import unittest
import sys
import json
from pathlib import Path
from PIL import Image

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from modules.distance_estimator import DistanceEstimator

class TestDistanceEstimator(unittest.TestCase):
    
    def setUp(self):
        self.image_width = 1000.0
        self.image_height = 1000.0
        self.estimator = DistanceEstimator() # uses defaults: near=0.40, medium=0.10

    def test_1_very_large_bbox(self):
        """Test 1: Very large bounding box. Expected: near"""
        # area = 800 * 800 = 640,000 (0.64 normalized)
        detections = [{"bbox": {"x1": 100, "y1": 100, "x2": 900, "y2": 900}}]
        result = self.estimator.estimate_proximity(detections, self.image_width, self.image_height)
        self.assertEqual(result[0]['distance']['proximity'], "near")
        self.assertAlmostEqual(result[0]['distance']['normalized_area'], 0.64)

    def test_2_medium_bbox(self):
        """Test 2: Medium-sized bounding box. Expected: medium"""
        # area = 500 * 500 = 250,000 (0.25 normalized)
        detections = [{"bbox": {"x1": 250, "y1": 250, "x2": 750, "y2": 750}}]
        result = self.estimator.estimate_proximity(detections, self.image_width, self.image_height)
        self.assertEqual(result[0]['distance']['proximity'], "medium")
        self.assertAlmostEqual(result[0]['distance']['normalized_area'], 0.25)

    def test_3_small_bbox(self):
        """Test 3: Small bounding box. Expected: far"""
        # area = 100 * 100 = 10,000 (0.01 normalized)
        detections = [{"bbox": {"x1": 450, "y1": 450, "x2": 550, "y2": 550}}]
        result = self.estimator.estimate_proximity(detections, self.image_width, self.image_height)
        self.assertEqual(result[0]['distance']['proximity'], "far")
        self.assertAlmostEqual(result[0]['distance']['normalized_area'], 0.01)

    def test_4_multiple_detections(self):
        """Test 4: Multiple detections. Verify independent proximity information."""
        detections = [
            {"bbox": {"x1": 100, "y1": 100, "x2": 900, "y2": 900}}, # near (0.64)
            {"bbox": {"x1": 250, "y1": 250, "x2": 750, "y2": 750}}, # medium (0.25)
            {"bbox": {"x1": 450, "y1": 450, "x2": 550, "y2": 550}}  # far (0.01)
        ]
        result = self.estimator.estimate_proximity(detections, self.image_width, self.image_height)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['distance']['proximity'], "near")
        self.assertEqual(result[1]['distance']['proximity'], "medium")
        self.assertEqual(result[2]['distance']['proximity'], "far")

    def test_5_different_resolutions(self):
        """Test 5: Different image resolutions. Verify consistent normalized area."""
        # bbox is 1/4 the area of the image in both cases
        # image 1: 1000x1000
        det1 = [{"bbox": {"x1": 0, "y1": 0, "x2": 500, "y2": 500}}]
        res1 = self.estimator.estimate_proximity(det1, 1000, 1000)
        self.assertAlmostEqual(res1[0]['distance']['normalized_area'], 0.25)
        self.assertEqual(res1[0]['distance']['proximity'], "medium")
        
        # image 2: 2000x500
        det2 = [{"bbox": {"x1": 0, "y1": 0, "x2": 1000, "y2": 250}}]
        res2 = self.estimator.estimate_proximity(det2, 2000, 500)
        self.assertAlmostEqual(res2[0]['distance']['normalized_area'], 0.25)
        self.assertEqual(res2[0]['distance']['proximity'], "medium")

    def test_6_boundary_touching(self):
        """Test 6: Bounding box touching image boundaries. Verify result is valid."""
        detections = [{"bbox": {"x1": 0, "y1": 0, "x2": 1000, "y2": 1000}}]
        result = self.estimator.estimate_proximity(detections, self.image_width, self.image_height)
        self.assertEqual(result[0]['distance']['proximity'], "near")
        self.assertAlmostEqual(result[0]['distance']['normalized_area'], 1.0)

    def test_7_out_of_bounds_bbox(self):
        """Test 7: Bounding box slightly outside boundaries. Verify clamping."""
        # bbox is slightly larger than the image (e.g. -10 to 1010)
        detections = [{"bbox": {"x1": -10, "y1": -50, "x2": 1050, "y2": 1010}}]
        result = self.estimator.estimate_proximity(detections, self.image_width, self.image_height)
        # Should clamp to 0-1000, making area = 1.0
        self.assertEqual(result[0]['distance']['proximity'], "near")
        self.assertAlmostEqual(result[0]['distance']['normalized_area'], 1.0)

    def test_8_invalid_width(self):
        """Test 8: Invalid image width."""
        detections = [{"bbox": {"x1": 100, "y1": 100, "x2": 200, "y2": 200}}]
        with self.assertRaises(ValueError):
            self.estimator.estimate_proximity(detections, 0, 1000)
        with self.assertRaises(ValueError):
            self.estimator.estimate_proximity(detections, -100, 1000)

    def test_9_invalid_height(self):
        """Test 9: Invalid image height."""
        detections = [{"bbox": {"x1": 100, "y1": 100, "x2": 200, "y2": 200}}]
        with self.assertRaises(ValueError):
            self.estimator.estimate_proximity(detections, 1000, 0)
        with self.assertRaises(ValueError):
            self.estimator.estimate_proximity(detections, 1000, -50)

    def test_10_invalid_bbox_x(self):
        """Test 10: Invalid bounding box where x2 < x1."""
        detections = [{"bbox": {"x1": 500, "y1": 100, "x2": 100, "y2": 200}}]
        with self.assertRaises(ValueError):
            self.estimator.estimate_proximity(detections, 1000, 1000)

    def test_11_invalid_bbox_y(self):
        """Test 11: Invalid bounding box where y2 < y1."""
        detections = [{"bbox": {"x1": 100, "y1": 500, "x2": 200, "y2": 100}}]
        with self.assertRaises(ValueError):
            self.estimator.estimate_proximity(detections, 1000, 1000)

    def test_12_zero_area(self):
        """Test 12: Zero-area bounding box."""
        detections = [{"bbox": {"x1": 100, "y1": 100, "x2": 100, "y2": 100}}]
        result = self.estimator.estimate_proximity(detections, 1000, 1000)
        self.assertEqual(result[0]['distance']['normalized_area'], 0.0)
        self.assertEqual(result[0]['distance']['proximity'], "far")


def test_real_yolo_integration():
    print("\n--- Real YOLO Integration Test ---")
    try:
        from modules.detector import YoloDetector
        detector = YoloDetector()
        
        test_image_path = backend_dir.parent / "test.jpg"
        print(f"Loading image from {test_image_path}")
        image = Image.open(test_image_path)
        img_width, img_height = image.size
        print(f"Image dimensions: {img_width}x{img_height}")
        
        raw_detections = detector.detect(image)
        print(f"Raw YOLO detections found: {len(raw_detections)}")
        
        estimator = DistanceEstimator()
        enriched_detections = estimator.estimate_proximity(raw_detections, img_width, img_height)
        
        print("\nEnriched Detections (Distance):")
        for det in enriched_detections:
            print(f"- Class: {det['class_name']}")
            print(f"  Bbox: {det['bbox']}")
            print(f"  Normalized Area: {det['distance']['normalized_area']}")
            print(f"  Area Ratio: {det['distance']['area_ratio_percent']}%")
            print(f"  Proximity: {det['distance']['proximity']}\n")
            
    except Exception as e:
        print(f"Failed Real YOLO test: {e}")

if __name__ == '__main__':
    # Run unit tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDistanceEstimator)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # Run real integration test
    if test_result.wasSuccessful():
        test_real_yolo_integration()
