# Generate single arucos Here:
# https://chev.me/arucogen/

import os
import numpy as np
import cv2

# ------------------------------
# ENTER YOUR PARAMETERS HERE:
ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 7
SQUARES_HORIZONTALLY = 5
SQUARE_LENGTH = 0.03
MARKER_LENGTH = 0.015
LENGTH_PX = 3300   # total width of the page in pixels (8.5 inches at 300 DPI)
HEIGHT_PX = 2550   # total height of the page in pixels (11 inches at 300 DPI)
MARGIN_PX = 20     # size of the margin in pixels
SAVE_NAME = 'Calibration/ChArUco_Marker.png'
# ------------------------------

def create_and_save_new_board():
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    board = cv2.aruco.CharucoBoard((SQUARES_VERTICALLY, SQUARES_HORIZONTALLY), SQUARE_LENGTH, MARKER_LENGTH, dictionary)
    img = cv2.aruco.CharucoBoard.generateImage(board, (LENGTH_PX, HEIGHT_PX), marginSize=MARGIN_PX)
    cv2.imshow("img", img)
    cv2.waitKey(2000)
    cv2.imwrite(SAVE_NAME, img)

create_and_save_new_board()
