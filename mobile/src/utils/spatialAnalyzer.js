// Ported from backend/modules/spatial_analyzer.py

export function spatialAnalyzer(detections, imageWidth = 640, imageHeight = 640) {
  const FRAME_CENTER_X = imageWidth / 2;
  // Center threshold represents the middle third of the frame
  const CENTER_THRESHOLD = imageWidth / 3; 

  const analyzed = detections.map(det => {
    const { x1, y1, x2, y2 } = det.bbox;
    
    // Calculate bounding box width and height
    const w = x2 - x1;
    const h = y2 - y1;
    
    // Calculate bounding box center
    const cx = x1 + (w / 2);
    const cy = y1 + (h / 2);
    
    // Calculate bounding box area
    const area = w * h;

    // Determine horizontal position
    let horizontal_position = "center";
    if (cx < FRAME_CENTER_X - (CENTER_THRESHOLD / 2)) {
      horizontal_position = "left";
    } else if (cx > FRAME_CENTER_X + (CENTER_THRESHOLD / 2)) {
      horizontal_position = "right";
    }

    // Determine vertical position
    let vertical_position = "center";
    if (cy < imageHeight / 3) {
      vertical_position = "top";
    } else if (cy > (2 * imageHeight) / 3) {
      vertical_position = "bottom";
    }

    // Heuristic Proximity Estimation based on normalized area
    const normalized_area = area / (imageWidth * imageHeight);
    
    let proximity = "medium";
    if (normalized_area > 0.4) {
      proximity = "near";
    } else if (normalized_area < 0.1) {
      proximity = "far";
    }

    return {
      ...det,
      spatial: {
        center_x: Math.round(cx),
        center_y: Math.round(cy),
        area: Math.round(area),
        horizontal_position,
        vertical_position
      },
      distance: {
        proximity,
        normalized_area: Number(normalized_area.toFixed(4))
      }
    };
  });

  return analyzed;
}
