import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import queue
import numpy as np
from math import atan
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Calibration import monitor_info
from Tools import fov_calculator







observer_fov = 150 # Human FOV
cube_distance = 0.25 # Distance cube is on other side of window
viewer_distance = 1 # distance in meters

# Define the size of the cube in meters
cube_size = 0.2  # Change this value to adjust the size of the cube



# Get monitor dimensions
monitor_width, monitor_height, monitor_dpi = monitor_info.get_monitor_dimensions()

# Global variables to store current state
x_translation = 0.0
y_translation = 0.0
fov = 45

running = True  # Flag to control the main loop

# Queue to communicate between threads
update_queue = queue.Queue()

def draw_cube():
    half_size = cube_size / 2
    vertices = [
        [half_size, half_size, -half_size],
        [half_size, half_size, half_size],
        [-half_size, half_size, half_size],
        [-half_size, half_size, -half_size],
        [half_size, -half_size, -half_size],
        [half_size, -half_size, half_size],
        [-half_size, -half_size, half_size],
        [-half_size, -half_size, -half_size]
    ]
    edges = [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7]
    ]
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    # Add more cubes to the scene
    glPushMatrix()
    glTranslatef(0.2, 0.2, -0.5)  # Move the cube to a new position
    glutSolidCube(0.1)  # Draw a smaller cube
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.3, -0.1, -0.6)  # Move the cube to another position
    glutSolidCube(0.15)  # Draw another smaller cube
    glPopMatrix()



def create_window():
    global x_translation, y_translation, viewer_distance, fov, running
    
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(fov, (display[0] / display[1]), 0.01, 500.0)

    while running:
        # Check for updates in the queue
        while not update_queue.empty():
            x_translation, y_translation, viewer_distance, fov = update_queue.get()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                return

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov, (display[0] / display[1]), 0.01, 500.0)
        glMatrixMode(GL_MODELVIEW)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Adjust the cube's position based on viewer's position
        cube_x_offset = (x_translation / monitor_width) * cube_distance/5
        cube_y_offset = (y_translation / monitor_height) * cube_distance/5

        # Calculate rotation angles based on viewer's position
        rotation_angle_x = (y_translation / monitor_height) * 20  # Rotate around X-axis based on Y position
        rotation_angle_y = (x_translation / monitor_width) * 20   # Rotate around Y-axis based on X position

        # Apply the transformations
        glTranslatef(cube_x_offset, -cube_y_offset, -viewer_distance)
        glRotatef(-rotation_angle_x, 1, 0, 0)  # Rotate around X-axis
        glRotatef(-rotation_angle_y, 0, 1, 0)  # Rotate around Y-axis


        draw_cube()
        pygame.display.flip()
        pygame.time.wait(10)
def update_perspective(x_position, y_position, distance):
    # Calculate new values
    new_x_translation = x_position
    new_y_translation = y_position
    new_fov = fov_calculator.calculate_window_fov(monitor_width, monitor_height, distance, observer_fov)
    new_viewer_distance = distance
    # Put the new values in the queue
    update_queue.put((new_x_translation, new_y_translation, new_viewer_distance, new_fov))


def asynchronous_create_window():
    threading.Thread(target=create_window).start()

if __name__ == "__main__":
    asynchronous_create_window()
    pygame.time.wait(6000)  # Give some time for the window to initialize
    # Example usage of update_perspective
    update_perspective(1.0, 1.0, 0.5)