import cv2
import numpy as np

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
    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    height_a = np.linalg.norm(tr - tl)
    height_b = np.linalg.norm(br - bl)
    max_width = max(int(width_a), int(width_b))
    max_height = max(int(height_a), int(height_b))
    aspect_ratio = 16 / 9
    if max_width / max_height > aspect_ratio:
        max_height = int(max_width / aspect_ratio)
    else:
        max_width = int(max_height * aspect_ratio)
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    return warped

def is_black_pixel(image, point):
    rgb = image[int(point[1]), int(point[0])]
    print(f"RGB at point {point}: {rgb}")
    return all(rgb < [25, 25, 25])

image = cv2.imread('Godot_test\input_image.png')
original = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

possible_rectangles = []
for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
    if len(approx) == 4 and all([is_black_pixel(original, pt[0]) for pt in approx]):
        possible_rectangles.append(contour)
        for pt in approx:
            cv2.circle(original, tuple(pt[0]), 5, (0, 255, 0), -1)
    else:
        for pt in approx:
            cv2.circle(original, tuple(pt[0]), 5, (0, 0, 255), -1)

if possible_rectangles:
    c = max(possible_rectangles, key=cv2.contourArea)
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)
    warped = transform_perspective(image, approx.reshape(4, 2))
    cv2.imwrite('Godot_test\cropped_image.png', warped)
else:
    print("No suitable rectangle found in the image.")

cv2.imshow('Marked Corners', original)
cv2.waitKey(0)
cv2.destroyAllWindows()
