import time
from ultralytics import YOLO

# Model Loading
model_path = r"d:\AI Indoor Navigation Assistant for Blind People\backend\models\best.pt"
print("--- Loading Model ---")
print(f"Path: {model_path}")

try:
    model = YOLO(model_path)
    print("Model loaded successfully.")
    
    print("\n--- Model Classes ---")
    classes = model.names
    for class_id, class_name in classes.items():
        print(f"ID: {class_id} -> {class_name}")

    # Inference Test
    test_image = r"d:\AI Indoor Navigation Assistant for Blind People\test.jpg"
    print("\n--- Real Inference Test ---")
    print(f"Test image path: {test_image}")
    
    start_time = time.time()
    results = model.predict(source=test_image, device="cpu", save=False)
    inference_time = time.time() - start_time
    
    print(f"\nInference completed in {inference_time:.4f} seconds.")
    
    for result in results:
        print(f"Original image shape (resolution): {result.orig_shape}")
        
        boxes = result.boxes
        print(f"Number of detections: {len(boxes)}")
        
        for box in boxes:
            class_id = int(box.cls[0])
            class_name = classes[class_id]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            
            print(f"- Detected: {class_name}, Confidence: {conf:.4f}, BBox: {xyxy}")

except Exception as e:
    print(f"Failed to load model or run inference. Error: {e}")
