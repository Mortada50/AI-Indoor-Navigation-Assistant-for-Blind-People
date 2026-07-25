// YOLOv8/11 Post-processing logic for TFLite output
// Tensor shape: [1, 15, 8400] (4 bbox + 11 classes, 8400 anchors)

const CONFIDENCE_THRESHOLD = 0.25;
const IOU_THRESHOLD = 0.45;

const CLASS_NAMES = [
  "cpu", "door", "keyboard", "monitor", "mouse",
  "blackboard", "chair", "laptop", "stairs", "table", "window"
];

function sigmoid(x) {
  return 1 / (1 + Math.exp(-x));
}

function computeIoU(box1, box2) {
  const x1 = Math.max(box1.x1, box2.x1);
  const y1 = Math.max(box1.y1, box2.y1);
  const x2 = Math.min(box1.x2, box2.x2);
  const y2 = Math.min(box1.y2, box2.y2);

  const intersectionArea = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
  const box1Area = (box1.x2 - box1.x1) * (box1.y2 - box1.y1);
  const box2Area = (box2.x2 - box2.x1) * (box2.y2 - box2.y1);
  const unionArea = box1Area + box2Area - intersectionArea;

  return intersectionArea / (unionArea || 1);
}

export function yoloPostProcess(outputTensor, imageWidth, imageHeight) {
  // outputTensor is a flat Float32Array of length 15 * 8400 = 126000
  // Structure: [xc_0, yc_0, w_0, h_0, p0_0, p1_0, ..., p10_0, xc_1, ...] or [xc_0...xc_8399, yc_0...yc_8399, ...]
  // Ultralytics exports default to: [batch, features, anchors] -> features = 4 (bbox) + 11 (classes) = 15
  // Memory layout in Float32Array: 15 rows, 8400 columns (flattened row-major)
  // So value at row i, col j is at index: i * 8400 + j

  const numClasses = 11;
  const numAnchors = 8400;
  let detections = [];

  for (let j = 0; j < numAnchors; j++) {
    let maxClassScore = -1;
    let classId = -1;

    // Find the class with the highest probability
    for (let i = 0; i < numClasses; i++) {
      // Index for class probability: (4 + i) * 8400 + j
      const score = outputTensor[(4 + i) * numAnchors + j];
      if (score > maxClassScore) {
        maxClassScore = score;
        classId = i;
      }
    }

    if (maxClassScore >= CONFIDENCE_THRESHOLD) {
      // Get bbox coordinates
      const xc = outputTensor[0 * numAnchors + j];
      const yc = outputTensor[1 * numAnchors + j];
      const w = outputTensor[2 * numAnchors + j];
      const h = outputTensor[3 * numAnchors + j];

      // Convert to x1, y1, x2, y2
      const x1 = xc - w / 2;
      const y1 = yc - h / 2;
      const x2 = xc + w / 2;
      const y2 = yc + h / 2;

      detections.push({
        class_id: classId,
        class_name: CLASS_NAMES[classId],
        confidence: maxClassScore,
        bbox: { x1, y1, x2, y2 }
      });
    }
  }

  // Non-Maximum Suppression (NMS)
  detections.sort((a, b) => b.confidence - a.confidence);
  const nmsDetections = [];
  
  while (detections.length > 0) {
    const current = detections.shift();
    nmsDetections.push(current);
    detections = detections.filter(d => {
      if (d.class_id !== current.class_id) return true; // Only apply NMS within the same class
      const iou = computeIoU(current.bbox, d.bbox);
      return iou < IOU_THRESHOLD;
    });
  }

  return nmsDetections;
}
