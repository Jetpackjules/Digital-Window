import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import queue

# Global variables to store current state
x_translation = 0.0
fov = 45
z_translation = -10
running = True  # Flag to control the main loop

# Queue to communicate between threads
update_queue = queue.Queue()


def draw_cube():
    vertices = [
        [1, 1, -1],
        [1, 1, 1],
        [-1, 1, 1],
        [-1, 1, -1],
        [1, -1, -1],
        [1, -1, 1],
        [-1, -1, 1],
        [-1, -1, -1]
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

def create_window():
    global x_translation, fov, z_translation
    
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    # Main loop in a separate thread
    def main_loop():
        global x_translation, fov, z_translation
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(fov, (display[0] / display[1]), 0.1, 50.0)
            glMatrixMode(GL_MODELVIEW)
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glTranslatef(x_translation, 0, z_translation)
            draw_cube()
            pygame.display.flip()
            pygame.time.wait(10)

    threading.Thread(target=main_loop).start()

def create_window():
    global x_translation, fov, z_translation, running
    
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)

    while running:
        # Check for updates in the queue
        while not update_queue.empty():
            x_translation, fov, z_translation = update_queue.get()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                return

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov, (display[0] / display[1]), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set the camera's position and orientation
        camera_x = x_translation
        camera_y = 0
        camera_z = z_translation
        gluLookAt(camera_x, camera_y, camera_z,  # Camera position
                  0, 0, 0,  # Look at the center of the cube
                  0, 1, 0)  # Up direction

        draw_cube()
        pygame.display.flip()
        pygame.time.wait(10)

def update_perspective(x_position, proximity):
    # Calculate new values
    new_x_translation = x_position
    new_fov = 45 - (proximity * 10)  # Adjust this formula as needed
    new_z_translation = -10 + (proximity * 2)  # Adjust this formula as needed

    # Put the new values in the queue
    update_queue.put((new_x_translation, new_fov, new_z_translation))

def asynchronous_create_window():
    threading.Thread(target=create_window).start()

if __name__ == "__main__":
    asynchronous_create_window()
    pygame.time.wait(1000)  # Give some time for the window to initialize
    # Example usage of update_perspective
    update_perspective(1.0, 0.5)

