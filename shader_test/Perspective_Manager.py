import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from PIL import Image
import numpy as np
import threading

fov = 150
X_offset = 0.0
Y_offset = 0.0
distance_to_monitor = 1.0
window_running = False
lock = threading.Lock()

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Calibration import monitor_info
from Tools import fov_calculator


monitor_width, monitor_height, monitor_dpi = monitor_info.get_monitor_dimensions() #Display size in meters, with pixels per inch as the last var


cubemap_images = [
    
    "Cubemap/posx.png",
    "Cubemap/negx.png",
    "Cubemap/posy.png",
    "Cubemap/negy.png",
    "Cubemap/posz.png",
    "Cubemap/negz.png"
]


def update(x, y, dist):
    global X_offset, Y_offset, distance_to_monitor, fov
    with lock:

        fov = 120
        # fov_calculator.calculate_window_fov(monitor_width, monitor_height, dist, 150)
        # print(dist)
        # print(monitor_width)

        # add webcam offset:
        offset = monitor_height/2


        X_offset = x
        Y_offset = y
        distance_to_monitor = dist
        if not window_running:
            threading.Thread(target=run_window).start()

def run_window():
    global window_running
    with lock:
        if window_running:
            return
        window_running = True

    # Set the FOV to 90 degrees
    fov = 90

    # Load one of the cubemap images to determine its dimensions
    image_sample = Image.open(cubemap_images[0])
    cubemap_width, cubemap_height = image_sample.size
    cubemap_aspect_ratio = cubemap_width / cubemap_height

    # Adjust the window's aspect ratio based on the cubemap and monitor dimensions
    aspect_ratio = monitor_width / monitor_height

    if cubemap_aspect_ratio > aspect_ratio:
        aspect_ratio = cubemap_aspect_ratio

    near_plane = 0.1
    far_plane = 1900.0
    q = 1.0 / np.tan(np.radians(0.5 * fov))
    a = q / aspect_ratio
    b = (near_plane + far_plane) / (near_plane - far_plane)
    c = (2.0 * near_plane * far_plane) / (near_plane - far_plane)
    projection = np.array([
        [a, 0, 0, 0],
        [0, q, 0, 0],
        [0, 0, b, -1],
        [0, 0, c, 0]
    ], dtype=np.float32)

    def lookAt(eye, center, up):
        f = (center - eye); f = f/np.linalg.norm(f)
        r = np.cross(up, f); r = r/np.linalg.norm(r)
        u = np.cross(f, r); u = u/np.linalg.norm(u)
        m = np.zeros((4, 4), dtype=np.float32)
        m[0, :-1] = r; m[0, -1] = -np.dot(r, eye)
        m[1, :-1] = u; m[1, -1] = -np.dot(u, eye)
        m[2, :-1] = -f; m[2, -1] = np.dot(f, eye)
        m[-1, -1] = 1.0
        return m

    def calculate_view_matrix(X_offset, Y_offset, distance_to_monitor):
        eye = np.array([X_offset, Y_offset, distance_to_monitor], dtype=np.float32)
        center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        return lookAt(eye, center, up)

    if not glfw.init():
        raise Exception("glfw can not be initialized!")
    

    
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)

    # Create the window with the monitor's dimensions
    window = glfw.create_window(int(monitor_width*100/2.54*monitor_dpi), int(monitor_height*100/2.54*monitor_dpi), "Cubemap Viewer", None, None)
 
    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created!")
    glfw.set_window_pos(window, 0, 0)
    glfw.make_context_current(window)


    cubemap = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap)
    for i, path in enumerate(cubemap_images):
        image = Image.open(path)
        img_data = image.tobytes()
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

    vertex_src = """
        #version 330
        layout(location = 0) in vec3 a_position;
        out vec3 v_texCoord;
        uniform mat4 u_projection;
        uniform mat4 u_view;
        void main()
        {
            v_texCoord = a_position;  
            gl_Position =  u_projection * u_view * vec4(a_position, 1.0);
        }
    """
    fragment_src = """
        #version 330
        in vec3 v_texCoord;
        out vec4 out_color;
        uniform samplerCube u_cubemap;
        void main()
        {
            out_color = texture(u_cubemap, v_texCoord);
        }
    """
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
    vertices = np.array([
        -1,  1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1,  1, -1, -1,  1, -1,
        -1, -1,  1, -1, -1, -1, -1,  1, -1, -1,  1, -1, -1,  1,  1, -1, -1,  1,
         1, -1, -1,  1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1,
        -1, -1,  1, -1,  1,  1,  1,  1,  1,  1,  1,  1,  1, -1,  1, -1, -1,  1,
        -1,  1, -1,  1,  1, -1,  1,  1,  1,  1,  1,  1, -1,  1,  1, -1,  1, -1,
        -1, -1, -1, -1, -1,  1,  1, -1, -1,  1, -1, -1, -1, -1,  1,  1, -1,  1
    ], dtype=np.float32)
    
    # Remove the fourth set of 18 vertices
    start_index = 3 * 18  # Starting index for the fourth set of 18 vertices
    end_index = start_index + 18  # Ending index
    vertices = np.delete(vertices, slice(start_index, end_index), axis=0)  # Remove the fourth set of 18 vertices
        
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize * 3, ctypes.c_void_p(0))
    while not glfw.window_should_close(window):
        glfw.poll_events()
        view = calculate_view_matrix(X_offset, Y_offset, distance_to_monitor)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)
        glUniformMatrix4fv(glGetUniformLocation(shader, "u_view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "u_projection"), 1, GL_FALSE, projection)
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glfw.swap_buffers(window)
    glfw.terminate()
    with lock:
        window_running = False



if __name__ == "__main__":
    update(0, 0, 1)
