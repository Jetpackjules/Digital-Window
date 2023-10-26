import cv2
import numpy as np
import tqdm

def resize_to_aspect_ratio(image, target_ratio=16/9, target_width=1280):
    """Resize the image to maintain the target aspect ratio."""
    h, w, _ = image.shape
    current_ratio = w / h

    if current_ratio > target_ratio:
        # Current aspect ratio is greater than target, adjust height
        new_height = int(w / target_ratio)
        padding_top = (new_height - h) // 2
        padding_bottom = new_height - h - padding_top
        image = cv2.copyMakeBorder(image, padding_top, padding_bottom, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
    elif current_ratio < target_ratio:
        # Current aspect ratio is less than target, adjust width
        new_width = int(h * target_ratio)
        padding_left = (new_width - w) // 2
        padding_right = new_width - w - padding_left
        image = cv2.copyMakeBorder(image, 0, 0, padding_left, padding_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    # Resize the image to the target width while maintaining the aspect ratio
    new_height = int(target_width / target_ratio)
    image = cv2.resize(image, (target_width, new_height))

    return image

def warp_to_aspect_ratio(image, target_ratio=16/9, target_width=1280):
    """Warp the image to maintain the target aspect ratio."""
    new_height = int(target_width / target_ratio)
    return cv2.resize(image, (target_width, new_height))

def order_points(pts):
    x_sorted = pts[np.argsort(pts[:, 0]), :]
    left = x_sorted[:2, :]
    right = x_sorted[2:, :]
    left = left[np.argsort(left[:, 1]), :]
    (tl, bl) = left
    d = np.linalg.norm(right - tl, axis=1)
    (br, tr) = right[np.argsort(d)[::-1]]
    return np.array([tl, tr, br, bl], dtype="float32")

def transform_perspective(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    width = max(int(np.linalg.norm(br - bl)), int(np.linalg.norm(tr - tl)))
    height = max(int(np.linalg.norm(tr - tl)), int(np.linalg.norm(br - bl)))
    dst = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (width, height))
    return warped

def is_black_pixel(image, point):
    rgb = image[int(point[1]), int(point[0])]
    return all(rgb < [25, 25, 25])\


# Load the video
cap = cv2.VideoCapture('Godot_test\input_video2.mp4')
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Initialize the VideoWriter with a placeholder size
out = None

# Get screen resolution
screen_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
screen_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Process each frame
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
for _ in tqdm.tqdm(range(frame_count), desc="Processing video"):
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    best_approx = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
        if len(approx) == 4 and cv2.contourArea(approx) > max_area:
            all_corners_black = all([is_black_pixel(frame, pt[0]) for pt in approx])
            if all_corners_black:
                max_area = cv2.contourArea(approx)
                best_approx = approx
    if best_approx is not None:
        warped = transform_perspective(frame, best_approx.reshape(4, 2))
        warped = warp_to_aspect_ratio(warped)

        # Resize the videos to fit within half the screen height
        target_height = int(screen_height / 2)
        frame_resized = cv2.resize(frame, (int(frame.shape[1] * target_height / frame.shape[0]), target_height))
        warped_resized = cv2.resize(warped, (int(warped.shape[1] * target_height / warped.shape[0]), target_height))

        # Ensure both frames have the same width
        min_width = min(frame_resized.shape[1], warped_resized.shape[1])
        frame_resized = frame_resized[:, :min_width]
        warped_resized = warped_resized[:, :min_width]

        # Concatenate the cropped and original frames vertically with cropped on top
        combined = np.vstack((warped_resized, frame_resized))
        
        cv2.imshow('Combined Frame', combined)
        
        # Initialize the VideoWriter with the correct size once we have the first combined frame
        if out is None:
            h, w, _ = combined.shape
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter('Godot_test\output_video2.mp4', fourcc, fps, (w, h))
        
        out.write(combined)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release everything
cap.release()
if out:
    out.release()
cv2.destroyAllWindows()