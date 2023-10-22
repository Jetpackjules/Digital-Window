import cv2
# import cv2.aruco as aruco
import numpy as np

#pip uninstall opencv-python
#pip install opencv-contrib-python==4.7.0.68

# Initialize the webcam feed
cap = cv2.VideoCapture(0)
    
# Set the resolution to 640x480 (adjust if needed)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Load the predefined dictionary
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Define the size of the ArUco marker in meters for pose estimation
markerLength = 0.05  # Adjust this value based on the actual size of your marker

# Approximate camera matrix for iPhone 12
fx = fy = 1400  # Approximate focal length
cx, cy = 640/2, 480/2  # Optical centers (principal points)
cameraMatrix = np.array([[fx, 0, cx],
                         [0, fy, cy],
                         [0, 0, 1]], dtype=np.float64)

# Approximate distortion coefficients (assuming no distortion)
distCoeffs = np.zeros((5,1), dtype=np.float64)

# Create default parameters and adjust some values
parameters = cv2.aruco.DetectorParameters()
parameters.adaptiveThreshWinSizeMin = 5
parameters.adaptiveThreshWinSizeMax = 23


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect ArUco markers
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

    # If any markers are detected, draw them on the frame and estimate their pose
    if len(corners) > 0:
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        
        # Estimate pose of each marker
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, distCoeffs)
        
        # Draw the rotation vectors on the frame
        for i in range(len(rvecs)):

            # Check the direction of the Z-axis (blue line)
            # Check the direction of the Z-axis (blue line) using the rotation vector
            if rvecs[i][0][2] < 0:
                rvecs[i][0][1] = -rvecs[i][0][1]

            
            frame = cv2.drawFrameAxes(frame, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 0.03)
            
            # Calculate the distance from the camera to the marker
            distance = np.linalg.norm(tvecs[i])
            
            # Define text properties
            text = f"Distance: {distance:.2f}m"
            font_scale = 1
            font_thickness = 2
            font_color = (0, 0, 255)  # RED
            bg_color = (0, 0, 0)  # BLACK
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            # Calculate text size
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
            
            # Define text and background rectangle positions
            text_offset_x = int(corners[i][0][0][0])
            text_offset_y = int(corners[i][0][0][1])
            box_coords = ((text_offset_x, text_offset_y + 5), (text_offset_x + text_width, text_offset_y - text_height - 5))
            
            # Draw a black background rectangle
            cv2.rectangle(frame, box_coords[0], box_coords[1], bg_color, cv2.FILLED)
            
            # Display the distance on the frame
            cv2.putText(frame, text, (text_offset_x, text_offset_y), font, font_scale, font_color, font_thickness, lineType=cv2.LINE_AA)

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cap.release()
cv2.destroyAllWindows()
