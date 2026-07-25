import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

print("Starting API Tests...")
time.sleep(2) # Give Flask time to start

# 1. Health Check
print("\n--- Testing GET /api/health ---")
r = requests.get(f"{BASE_URL}/health")
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}")

# 2. Missing Image
print("\n--- Testing POST /api/detect (Missing Image) ---")
r = requests.post(f"{BASE_URL}/detect")
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}")

# 3. Invalid Image
print("\n--- Testing POST /api/detect (Invalid Image) ---")
with open(r"d:\AI Indoor Navigation Assistant for Blind People\test.txt", "rb") as f:
    files = {"image": f}
    r = requests.post(f"{BASE_URL}/detect", files=files)
print(f"Status Code: {r.status_code}")
print(f"Response: {r.text}")

# 4. Valid Image (test.jpg) - Request 1
print("\n--- Testing POST /api/detect (Valid Image test.jpg) - Request 1 ---")
with open(r"d:\AI Indoor Navigation Assistant for Blind People\test.jpg", "rb") as f:
    files = {"image": f}
    start = time.time()
    r1 = requests.post(f"{BASE_URL}/detect", files=files)
    elapsed1 = time.time() - start
print(f"Status Code: {r1.status_code}")
print(f"Time Taken (Req 1): {elapsed1:.2f}s")

# 5. Valid Image (test.jpg) - Request 2
print("\n--- Testing POST /api/detect (Valid Image test.jpg) - Request 2 ---")
with open(r"d:\AI Indoor Navigation Assistant for Blind People\test.jpg", "rb") as f:
    files = {"image": f}
    start = time.time()
    r2 = requests.post(f"{BASE_URL}/detect", files=files)
    elapsed2 = time.time() - start
print(f"Status Code: {r2.status_code}")
print(f"Time Taken (Req 2): {elapsed2:.2f}s")

print(f"\nTime Difference: {elapsed1 - elapsed2:.2f}s (Proves Model Cache/Reuse)")

try:
    data = r2.json()
    print("\nResponse JSON Keys:", data.keys())
    print("Success:", data.get("success"))
    
    scene_inference = data.get("scene_inference", {})
    print(f"\nScene Inference Result:")
    print(json.dumps(scene_inference, indent=2, ensure_ascii=False))
    
    guidance = data.get("guidance", {})
    print(f"\nGuidance Result:")
    print(json.dumps(guidance, indent=2, ensure_ascii=False))
    
    detections = data.get("detections", [])
    print(f"\nNumber of detections: {len(detections)}")
    if detections:
        print("First Detection:", json.dumps(detections[0], indent=2))
        print("Second Detection:", json.dumps(detections[1], indent=2))
except Exception as e:
    print(f"Failed to parse JSON response: {e}")
    print(r2.text)

print("\n--- API Tests Completed ---")
