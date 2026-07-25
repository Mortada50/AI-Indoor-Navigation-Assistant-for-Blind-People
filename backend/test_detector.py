import sys
import json
import time
from pathlib import Path

# Add backend directory to sys.path to allow importing from modules
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from modules.detector import YoloDetector

def run_test():
    print("=== YOLO Detector Independent Test ===")
    
    # 1. Initialization
    print("\n1. Initializing Detector...")
    start_init = time.time()
    try:
        detector = YoloDetector()
        print(f"   Success! Model loaded from: {detector.model_path}")
        print(f"   Initialization time: {time.time() - start_init:.4f} seconds")
    except Exception as e:
        print(f"   FAILED to initialize: {e}")
        return

    # 2. Dynamic Class Names
    print("\n2. Checking Dynamic Class Names...")
    print(f"   Total classes found: {len(detector.class_names)}")
    print(f"   Sample classes: {list(detector.class_names.items())[:5]} ...")

    # 3. First Inference Call
    test_image_path = str(backend_dir.parent / "test.jpg")
    print(f"\n3. Running First Inference on {test_image_path}...")
    try:
        start_inf1 = time.time()
        results1 = detector.detect(image_input=test_image_path, conf_threshold=0.25, device="cpu")
        print(f"   Success! Inference time: {time.time() - start_inf1:.4f} seconds")
        print(f"   Found {len(results1)} detections.")
        if results1:
            print("   Sample Result (Structured Format):")
            print(json.dumps(results1[0], indent=2))
    except Exception as e:
        print(f"   FAILED inference 1: {e}")
        return

    # 4. Second Inference Call (Verify Reusability)
    print("\n4. Running Second Inference (Reusability Test)...")
    try:
        start_inf2 = time.time()
        results2 = detector.detect(image_input=test_image_path, conf_threshold=0.50, device="cpu")
        print(f"   Success! Inference time: {time.time() - start_inf2:.4f} seconds")
        print(f"   Found {len(results2)} detections (with conf >= 0.50).")
    except Exception as e:
        print(f"   FAILED inference 2: {e}")
        return

    print("\n=== Test Completed Successfully ===")

if __name__ == "__main__":
    run_test()
