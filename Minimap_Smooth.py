import cv2
import numpy as np
from collections import deque

# Define the size of the deque for smoothing
SMOOTHING_SIZE = 5
yaw_values = deque(maxlen=SMOOTHING_SIZE)


#important variables:
markerLength = 0.1 #meters

# Minimap resolution
MINIMAP_WIDTH = 720
MINIMAP_HEIGHT = 1080

#shrink resolution?
shrink = True


# Camera resolution
cap = cv2.VideoCapture(0)
WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Change this to your desired width
HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Change this to your desired height
print(f"Detected webcam resolution: {WIDTH}x{HEIGHT}")

def draw_arrow(image, position, angle):
    length = 50
    end_x = int(position[0] + length * np.sin(angle))
    end_y = int(position[1] - length * np.cos(angle))
    cv2.arrowedLine(image, position, (end_x, end_y), (0, 0, 255), 2)

if shrink:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    WIDTH = 640
    HEIGHT = 480

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)


dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)


fx = fy = 1400  # This is a rough estimate and might need adjustment
cx = WIDTH / 2
cy = HEIGHT / 2

cameraMatrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
distCoeffs = np.zeros((5,1), dtype=np.float64)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary)
    mirrored_frame = cv2.flip(frame, 1)  # Create a mirrored version for display


    mini_map = np.zeros((MINIMAP_HEIGHT, MINIMAP_WIDTH, 3), dtype=np.uint8)


    if len(corners) > 0:
        for corner in corners:
            corner[:, :, 0] = frame.shape[1] - corner[:, :, 0]
        
        mirrored_frame = cv2.aruco.drawDetectedMarkers(mirrored_frame, corners, ids)  # Draw on the mirrored frame

        # frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, markerLength, cameraMatrix, distCoeffs)

        # For simplicity, consider the first detected marker for the mini-map
        rvec = rvecs[0]
        tvec = tvecs[0]
        # After estimating the pose:
        # rvec = rvecs[0]

        # Check and adjust the Z component of the rotation vector
        print("Shape of rvec:", rvec.shape)
        print("rvec:", rvec)
        if rvec[0][1] < 0:
            rvec[0][1] = -rvec[0][1]
        
        # Convert rotation vector to Euler angles for 2D rotation
        yaw = -cv2.Rodrigues(rvec)[0][2][0]
        # Inside the loop, after calculating the yaw:
        yaw_values.append(yaw)
        smoothed_yaw = sum(yaw_values) / len(yaw_values)

        # Calculate arrow's position on the minimap
        position_x = int((MINIMAP_WIDTH/2 + tvec[0][0] * MINIMAP_WIDTH/2))  # Centered and scaled
        position_y = int(tvec[0][2] * MINIMAP_HEIGHT/2)


        # Adjust x position based on distance to camera to account for the vision cone effect
        fov_adjustment = (1 - tvec[0][2]) * (MINIMAP_WIDTH/2 - position_x) * 0.5

        position_x += int(fov_adjustment)

        position = (position_x, position_y)

        draw_arrow(mini_map, position, smoothed_yaw)


        # Draw the rotation vectors on the frame
        for i in range(len(rvecs)):
            mirrored_frame = cv2.drawFrameAxes(mirrored_frame, cameraMatrix, distCoeffs, rvecs[i], tvecs[i], 0.03)
            
            # Calculate the distance from the camera to the marker
            distance = np.linalg.norm(tvecs[i])
            
            # Define text properties
            text = f"Distance: {distance:.2f}m"
            font_scale = 0.5
            font_thickness = 1
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
            cv2.rectangle(mirrored_frame, box_coords[0], box_coords[1], bg_color, cv2.FILLED)
            
            # Display the distance on the frame
            cv2.putText(mirrored_frame, text, (text_offset_x, text_offset_y), font, font_scale, font_color, font_thickness, lineType=cv2.LINE_AA)

    
    cv2.imshow('Frame', mirrored_frame)
    cv2.imshow('Mini-Map', mini_map)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
