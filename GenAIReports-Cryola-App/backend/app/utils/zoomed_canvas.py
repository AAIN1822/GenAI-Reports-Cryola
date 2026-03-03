import cv2
import numpy as np

def create_zoomed_canvas(
    input_bytes,
    canvas_width=6600,
    canvas_height=5100,
    zoom_factor=0.7,
):
    image_array = np.frombuffer(input_bytes, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Image decode failed")

    # Processing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    coords = cv2.findNonZero(thresh)
    if coords is None:
        raise ValueError("No object detected in image")
    
    x, y, w, h = cv2.boundingRect(coords)
    cropped = img[y:y+h, x:x+w]
    
    h, w = cropped.shape[:2]
    scale = min(canvas_width / w, canvas_height / h)
    
    new_w = int(w * scale * zoom_factor)
    new_h = int(h * scale * zoom_factor)
    
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    resized = cv2.filter2D(resized, -1, kernel)    
    
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
    
    x_offset = (canvas_width - new_w) // 2
    y_offset = (canvas_height - new_h) // 2
    
    if x_offset < 0 or y_offset < 0:
        resized = resized[
            max(0, -y_offset):min(new_h, canvas_height - y_offset),
            max(0, -x_offset):min(new_w, canvas_width - x_offset)
        ]
        x_offset = max(0, x_offset)
        y_offset = max(0, y_offset)
        
    canvas[
        y_offset:y_offset+resized.shape[0],
        x_offset:x_offset+resized.shape[1]
    ] = resized
    
    _, buffer = cv2.imencode(".jpg", canvas)
    return buffer.tobytes()
