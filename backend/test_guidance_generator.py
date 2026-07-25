import unittest
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from modules.guidance_generator import GuidanceGenerator

class TestGuidanceGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = GuidanceGenerator()

    def _make_det(self, name, h_pos, prox):
        return {
            "class_name": name,
            "spatial": {"horizontal_position": h_pos},
            "distance": {"proximity": prox}
        }

    # 1. Single object on left.
    def test_single_object_left(self):
        dets = [self._make_det("Door", "left", "medium")]
        res = self.generator.generate(dets)
        self.assertIn("باب", res["summary"])
        self.assertIn("اليسار", res["summary"])
        self.assertNotIn("أمتار", res["summary"])

    # 2. Single object in center.
    def test_single_object_center(self):
        dets = [self._make_det("table", "center", "near")]
        res = self.generator.generate(dets)
        self.assertIn("طاولة", res["summary"])
        self.assertIn("أمامك", res["summary"])

    # 3. Single object on right.
    def test_single_object_right(self):
        dets = [self._make_det("chair", "right", "far")]
        res = self.generator.generate(dets)
        self.assertIn("كرسي", res["summary"])
        self.assertIn("اليمين", res["summary"])

    # 4. Near object.
    def test_near_object(self):
        dets = [self._make_det("laptop", "center", "near")]
        res = self.generator.generate(dets)
        self.assertIn("قريب", res["summary"])

    # 5. Medium proximity object.
    def test_medium_object(self):
        dets = [self._make_det("window", "left", "medium")]
        res = self.generator.generate(dets)
        self.assertIn("متوسط القرب", res["summary"])

    # 6. Far object.
    def test_far_object(self):
        dets = [self._make_det("stairs", "right", "far")]
        res = self.generator.generate(dets)
        self.assertIn("بعيد", res["summary"])

    # 7. Multiple different objects.
    def test_multiple_objects(self):
        dets = [
            self._make_det("stairs", "center", "far"),
            self._make_det("chair", "left", "near")
        ]
        res = self.generator.generate(dets)
        self.assertIn("درج", res["summary"])
        self.assertIn("كرسي", res["summary"])

    # 8. Duplicate objects.
    def test_duplicate_objects(self):
        dets = [
            self._make_det("chair", "left", "near"),
            self._make_det("chair", "left", "near"),
            self._make_det("chair", "left", "near")
        ]
        res = self.generator.generate(dets)
        self.assertIn("3", res["summary"])
        self.assertIn("كرسي", res["summary"])

    # 9. Classroom scene.
    def test_classroom_scene(self):
        dets = [self._make_det("blackboard", "center", "medium")]
        res = self.generator.generate(dets, {"scene": "Classroom"})
        self.assertIn("قاعة دراسية", res["summary"])

    # 10. Computer Laboratory scene.
    def test_computer_lab_scene(self):
        dets = [self._make_det("CPU", "center", "medium")]
        res = self.generator.generate(dets, {"scene": "Computer Laboratory"})
        self.assertIn("معمل حاسوب", res["summary"])

    # 11. Unknown scene.
    def test_unknown_scene(self):
        dets = [self._make_det("Door", "center", "medium")]
        res = self.generator.generate(dets, {"scene": "Unknown Indoor Space"})
        self.assertNotIn("بيئة داخلية غير محددة", res["summary"]) # It shouldn't actively say "you are in an unknown space"

    # 12. Empty detections.
    def test_empty_detections(self):
        res = self.generator.generate([])
        self.assertEqual(len(res["messages"]), 0)
        self.assertIn("لم يتم اكتشاف", res["summary"])

    # 13. Unknown class name.
    def test_unknown_class(self):
        dets = [self._make_det("AlienSpaceship", "center", "medium")]
        res = self.generator.generate(dets)
        self.assertIn("alienspaceship", res["summary"]) # Fallback to original

    # 14. Missing optional scene inference.
    def test_missing_scene(self):
        dets = [self._make_det("chair", "center", "medium")]
        res = self.generator.generate(dets, scene_inference=None)
        self.assertNotIn("أنت في", res["summary"])

    # 15. Malformed detection input.
    def test_malformed_detections(self):
        dets = [
            {"invalid_key": "data"}, # completely invalid
            {"class_name": "Door"}, # missing spatial/distance
            self._make_det("chair", "left", "near") # valid
        ]
        res = self.generator.generate(dets)
        self.assertEqual(len(res["messages"]), 1)
        self.assertIn("كرسي", res["summary"])

    # 16. Door priority.
    def test_door_priority(self):
        dets = [
            self._make_det("chair", "center", "near"),
            self._make_det("Door", "right", "far")
        ]
        res = self.generator.generate(dets)
        # Priority should place Door first
        self.assertTrue(res["messages"][0].startswith("يوجد باب"))

    # 17. Stairs priority.
    def test_stairs_priority(self):
        dets = [
            self._make_det("table", "center", "near"),
            self._make_det("stairs", "left", "far")
        ]
        res = self.generator.generate(dets)
        self.assertTrue(res["messages"][0].startswith("يوجد درج"))

    # 18. Near object priority.
    def test_near_priority(self):
        dets = [
            self._make_det("table", "right", "far"),
            self._make_det("chair", "left", "near")
        ]
        res = self.generator.generate(dets)
        self.assertTrue(res["messages"][0].startswith("يوجد كرسي"))

    # 19. Arabic output is generated correctly.
    def test_arabic_charset(self):
        dets = [self._make_det("table", "right", "far")]
        res = self.generator.generate(dets)
        self.assertTrue(any('\u0600' <= c <= '\u06FF' for c in res["summary"]))

    # 20. The module never outputs physical distances in meters or centimeters.
    def test_no_physical_distance(self):
        dets = [self._make_det("Door", "center", "near")]
        res = self.generator.generate(dets)
        self.assertNotIn("متر", res["summary"])
        self.assertNotIn("سنتيمتر", res["summary"])
        self.assertNotIn("meter", res["summary"].lower())

if __name__ == '__main__':
    unittest.main()
