import os
import numpy as np
import cv2

# ------------------------------
# ENTER YOUR PARAMETERS HERE:
ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 7
SQUARES_HORIZONTALLY = 5
SQUARE_LENGTH = 0.036
MARKER_LENGTH = 0.018
# ...
PATH_TO_YOUR_IMAGES = 'Calibration/Images'

NAME = "Desktop_Webcam" # cam name
# ------------------------------

def calibrate_and_save_parameters():
    # Define the aruco dictionary and charuco board
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    params = cv2.aruco.DetectorParameters()

    # Load PNG images from folder
    image_files = [os.path.join(PATH_TO_YOUR_IMAGES, f) for f in os.listdir(PATH_TO_YOUR_IMAGES) if f.endswith(".jpg")]
    image_files.sort()  # Ensure files are in order

    all_charuco_corners = []
    all_charuco_ids = []

    for image_file in image_files:
        image = cv2.imread(image_file)
        image_copy = image.copy()
        marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(image, dictionary, parameters=params)
        
        # If at least one marker is detected

        if (marker_ids is not None):
            if(len(marker_ids) > 0):
                cv2.aruco.drawDetectedMarkers(image_copy, marker_corners, marker_ids)
                charuco_retval, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(marker_corners, marker_ids, image, board)
                if charuco_retval:
                    all_charuco_corners.append(charuco_corners)
                    all_charuco_ids.append(charuco_ids)

    # Calibrate camera
    min_corners_required = 4
    valid_views = [i for i, corners in enumerate(all_charuco_corners) if len(corners) >= min_corners_required]

    all_charuco_corners = [all_charuco_corners[i] for i in valid_views]
    all_charuco_ids = [all_charuco_ids[i] for i in valid_views]

    retval, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(all_charuco_corners, all_charuco_ids, board, image.shape[:2], None, None)

    # Save calibration data
    np.save('Calibration/'+NAME+'camera_matrix.npy', camera_matrix)
    np.save('Calibration/'+NAME+'dist_coeffs.npy', dist_coeffs)

    # Iterate through displaying all the images
    for image_file in image_files:
        image = cv2.imread(image_file)
        undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs)
        cv2.imshow('Undistorted Image', undistorted_image)
        cv2.waitKey(1000)

    cv2.destroyAllWindows()

calibrate_and_save_parameters()