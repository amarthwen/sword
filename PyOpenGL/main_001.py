# taken from https://cyrille.rossant.net/2d-graphics-rendering-tutorial-with-pyopengl/

import sys

# PyQt5 imports
from PyQt5 import QtWidgets
from PyQt5.QtOpenGL import QGLWidget

# PyOpenGL imports
import OpenGL.GL as gl

class GLPlotWidget(QGLWidget):
    # default window size
    width, height = 800, 600

    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(1,1,1,0)

    def drawRectangle(self, x, y, width, height, color, line_width):
        # set black color for subsequent drawing rendering calls
        gl.glColor(0,0,0)

        # draw rectangle
        gl.glBegin(gl.GL_QUADS);
        gl.glVertex2f(x - line_width, y - line_width);
        gl.glVertex2f(x + width + line_width, y - line_width);
        gl.glVertex2f(x + width + line_width, y + height + line_width);
        gl.glVertex2f(x - line_width, y + height + line_width);
        gl.glEnd();

        # set color for subsequent drawing rendering calls
        gl.glColor(color[0], color[1], color[2])

        # draw rectangle
        gl.glBegin(gl.GL_QUADS);
        gl.glVertex2f(x, y);
        gl.glVertex2f(x + width, y);
        gl.glVertex2f(x + width, y + height);
        gl.glVertex2f(x, y + height);
        gl.glEnd();

    def paintGL(self):
        """Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        tmp_list = (
            ('Adam', 930, 130),
            ('Set', 912, 105),
            ('Enosz', 905, 90),
            ('Kenan', 910, 70),
            ('Mahalalel', 895, 65),
            ('Jered', 962, 162),
            ('Henoch', 365, 65),
            ('Metuszelach', 969, 187),
            ('Lamech', 777, 182),
            ('Noe', 950, 500),
            ('Sem', 600, 100),
            ('Arpachszad', 438, 35),
            ('Szelach', 433, 30),
            ('Heber', 464, 34),
            ('Peleg', 239, 30),
            ('Reu', 239, 32),
            ('Serug', 230, 30),
            ('Nachor', 148, 29),
            ('Terah', 205, 70),
            ('Abram', 175, 100),
            ('Izaak', 180, 60),
            ('Jakub', 147, 91),
            ('Jozef', 110, 37)
        )

        tmp_year = 0
        tmp_distance_y = 20
        tmp_height = 16
        tmp_offset = 10
        tmp_scale = 2.0/5.0
        i = 0

        for entry in tmp_list:
            # print entry[0] + '/' + str(entry[1]) + '/' + str(entry[2])
            self.drawRectangle(tmp_offset + tmp_year * tmp_scale, tmp_offset + i * tmp_distance_y, entry[1] * tmp_scale, tmp_height, (0.5, 0.75, 0.95), 1)
            self.drawRectangle(tmp_offset + tmp_year * tmp_scale, tmp_offset + i * tmp_distance_y, entry[2] * tmp_scale, tmp_height, (1, 1, 0.75), 0)
            i += 1
            tmp_year += entry[2]

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        # paint within the whole window
        gl.glViewport(0, 0, width, height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        # the window corner OpenGL coordinates are (-+1, -+1)
        gl.glOrtho(0, width, height, 0, -1, 1)

# define a Qt window with an OpenGL widget inside it
class TestWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(TestWindow, self).__init__()
        # initialize the GL widget
        self.widget = GLPlotWidget()
        # put the window at the screen position (100, 100)
        self.setGeometry(100, 100, self.widget.width, self.widget.height)
        self.setCentralWidget(self.widget)
        self.show()

if __name__ == '__main__':
    # create the Qt App and window
    app = QtWidgets.QApplication(sys.argv)
    window = TestWindow()
    window.show()
    app.exec_()

