import cv2
import dlib
import numpy as np

# Load dlib's face detector
detector = dlib.get_frontal_face_detector()

# Load the panoramic image
panorama = cv2.imread('bryan-goff-IuyhXAia8EA-unsplash.jpg')

# Initialize webcam
cap = cv2.VideoCapture(0)

window_width = 640  # Define the width of the window
window_height = 480  # Define the height of the window

# Smoothing parameters
smoothing_factor = 0.9
smoothed_x_offset = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = detector(gray)

    for face in faces:
        coords = face.center()

        # Calculate the offset from the center
        x_offset = (coords.x - frame.shape[1] / 2) / frame.shape[1]

        # Apply smoothing
        smoothed_x_offset = smoothed_x_offset * smoothing_factor + x_offset * (1 - smoothing_factor)

        # Calculate which part of the panoramic image to display based on the smoothed offset
        start_x = int((panorama.shape[1] - window_width) * (smoothed_x_offset + 0.5))
        end_x = start_x + window_width
        displayed_image = panorama[:window_height, start_x:end_x]

        cv2.imshow("Window View", displayed_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
