import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QOpenGLContext, QOpenGLShader, QOpenGLShaderProgram, QOpenGLVersionProfile
import numpy as np
import OpenGL.GL as gl
from PyQt5.QtGui import QSurfaceFormat, QOpenGLContext

class CubeVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the app and set up the OpenGL context
        self.app = QApplication(sys.argv)
        self.context = QOpenGLContext(self)
        self.profile = QOpenGLVersionProfile()
        self.profile.setVersion(2, 0)
        self.context.setFormat(QSurfaceFormat.defaultFormat())
        format = QSurfaceFormat()
        format.setProfile(QSurfaceFormat.NoProfile)  # Set the desired profile
        self.context.setFormat(format)
        # self.context.setProfile(QOpenGLContext.NoProfile)
        self.context.create()
        # self.context.aboutToBeDestroyed.connect(self.cleanUpGl)

        # Set up the OpenGL window
        self.setFixedSize(800, 600)
        self.setWindowTitle('Cube Visualizer')
        self.cubeWidget = QOpenGLWidget(self)
        self.setCentralWidget(self.cubeWidget)
        self.cubeWidget.setFixedSize(800, 600)
        self.cubeWidget.initializeGL = self.initializeGL
        self.cubeWidget.resizeGL = self.resizeGL
        self.cubeWidget.paintGL = self.paintGL

        # Set up the rotation variables
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        # Timer to update the cube's rotation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateRotation)
        self.timer.start(16)  # 60 FPS

        # Show the window
        self.show()

        # Allow the PyQt5 event loop to process events without blocking
        self.app.processEvents()

    def setRotation(self, x, y, z):
        self.xRot = x
        self.yRot = y
        self.zRot = z

    def updateRotation(self):
        self.cubeWidget.update()

    def initializeGL(self):
        # Set up the shaders and program
        vertexShaderSource = """
            #version 120
            attribute vec4 vertex;
            uniform mat4 matrix;
            void main(void) {
                gl_Position = matrix * vertex;
            }
        """
        fragmentShaderSource = """
            #version 120
            void main(void) {
                gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
            }
        """
        self.vertexShader = QOpenGLShader(QOpenGLShader.Vertex, self)
        self.vertexShader.compileSourceCode(vertexShaderSource)
        self.fragmentShader = QOpenGLShader(QOpenGLShader.Fragment, self)
        self.fragmentShader.compileSourceCode(fragmentShaderSource)
        self.shaderProgram = QOpenGLShaderProgram(self)
        self.shaderProgram.addShader(self.vertexShader)
        self.shaderProgram.addShader(self.fragmentShader)
        self.shaderProgram.link()
        self.shaderProgram.bind()

        # Set up the cube data
        self.vertices = np.array([
            [-0.5, -0.5, -0.5],
            [0.5, -0.5, -0.5],
            [0.5, 0.5, -0.5],
            [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5],
            [0.5, -0.5, 0.5],
            [0.5, 0.5, 0.5],
            [-0.5, 0.5, 0.5]
        ], dtype=np.float32)
        self.indices = np.array([
            0, 1, 2, 3,
            4, 5, 6, 7,
            0, 1, 5, 4,
            2, 3, 7, 6,
            0, 3, 7, 4,
            1, 2, 6, 5
        ], dtype=np.uint32)
        # Enable depth testing
        gl.glEnable(gl.GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        # Set up the viewport and perspective
        gl.glViewport(0, 0, w, h)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # Use perspective projection instead of orthographic
        aspectRatio = w / h
        gl.glFrustum(-aspectRatio, aspectRatio, -1, 1, 1, 10)

        gl.glMatrixMode(gl.GL_MODELVIEW)



    def paintGL(self):
        # Clear the screen and draw the cube
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()

        # Move the cube a bit further away from the camera
        gl.glTranslatef(0.0, 0.0, -3.0)

        # Apply rotations
        gl.glRotatef(self.xRot, 1, 0, 0)
        gl.glRotatef(self.yRot, 0, 1, 0)
        gl.glRotatef(self.zRot, 0, 0, 1)

        # Draw the cube
        gl.glBegin(gl.GL_QUADS)
        for i in self.indices:
            gl.glVertex3fv(self.vertices[i])
        
        gl.glEnd()
        self.checkGLError()
        

    def run(self):
        # Start the PyQt5 event loop
        sys.exit(self.app.exec_())

    def checkGLError(self):
        error = gl.glGetError()
        if error != gl.GL_NO_ERROR:
            print(f"OpenGL Error: {error}")

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create QApplication object here
    cube = CubeVisualizer()
    cube.run()







