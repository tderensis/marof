import sys, signal, threading, select

from OpenGL.GL import *
from PyQt4.QtCore import SIGNAL, Qt
from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QLineEdit, QPushButton, QLabel, 
                         QFormLayout, QGridLayout, QVBoxLayout)
from PyQt4.QtOpenGL import QGLWidget

import lcm
from marof import getMicroSeconds
from marof_lcm import orientation_t

class GLOrientation(QGLWidget):
    """ Display the orientation of a vehicle. """
    
    def __init__(self, parent=None):
        super(GLOrientation, self).__init__(parent)
        self.setMinimumSize(300, 300)
        self._roll = 0
        self._pitch = 0
        self._yaw = 0
        self._cameraAngle = 30
        
    def turnLeft(self):
        self._cameraAngle = (self._cameraAngle + 2)%360
        
    def turnRight(self):
        self._cameraAngle = (self._cameraAngle - 2)%360
    
    def setOrientation(self, roll, pitch, heading):
        self._roll = roll
        self._pitch = pitch
        self._yaw = heading
            
    def drawGrid(self, x, y, z, res):
        glPushMatrix()
        glColor3f(0.25, 0.25, 0.25)

        dy = -y
        while dy < y:
            dx = -x
            while dx < x:
                glBegin(GL_LINES)
                glVertex3f(dx, dy, -z)
                glVertex3f(dx, dy, z)
                glEnd()
                dx += res
            dy += res
                
        dz = -z
        while dz < z:
            dx = -x
            while dx < x:
                glBegin(GL_LINES)
                glVertex3f(dx, -y, dz)
                glVertex3f(dx, y, dz)
                glEnd()
                dx += res
            dz += res
        
        dy = -y
        while dy < y:
            dz = -z
            while dz < z:
                glBegin(GL_LINES)
                glVertex3f(-x, dy, dz)
                glVertex3f(x, dy, dz)
                glEnd()
                dz += res
            dy += res
        glPopMatrix()
    
    def drawAxes(self):
        glPushMatrix()
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1, 0)
        glEnd()
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(1, 0, 0)
        glEnd()
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -1)
        glEnd()
        glPopMatrix()
    
    def drawBodyAxes(self):
        glPushMatrix()
        glRotated(self._roll, 0, 1, 0)
        glRotated(self._pitch, 1, 0, 0)
        glRotated(self._yaw, 0, 0, -1)
        glLineWidth(5.0)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0.75, 0)
        glEnd()
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0.75, 0, 0)
        glEnd()
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -0.75)
        glEnd()
        glLineWidth(1.0)
        glPopMatrix()
            
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        
        # Set up camera angle
        glRotated(20, -1, 0, 0)
        glRotated(self._cameraAngle, 0, 0, 1)
        
        self.drawGrid(2.0, 2.0, 2.0, 0.5)
        self.drawAxes()
        self.drawBodyAxes()
        glPopMatrix()
        
        
          
    def resizeGL(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1.5, 1.5, -1.5, 1.5, -1.5, 1.5)
        glViewport(0, 0, w, h)
    
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)


class MarofGui(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('MARoF GUI')
        self._isKilled = True
        self._speed = 0.0
        self._turn = 0.0
        self._lcm = lcm.LCM()
        self._lcm.subscribe("ORIENTATION", self.handleOrientation)
        self.createMainFrame()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # Stop the program if CTRL-C is received
        self._stopEvent = threading.Event()
        
        self.handlerThread = threading.Thread(target=self.pollLcm)
        self.handlerThread.setDaemon(True)
        self.handlerThread.start()
        
    def _cleanup(self):
        self._stopEvent.set()
        self.handlerThread.join()
        
    def pollLcm(self):
        while not self._stopEvent.isSet():
            try:
                rc = select.select([self._lcm.fileno()], [], [self._lcm.fileno()], 0.05)
            except:
                break
            if len(rc[0]) > 0 or len(rc[2]) > 0:
                self._lcm.handle()
                
    def handleOrientation(self, channel, encoded):
        print "got"
        msg = orientation_t().decode(encoded)
        self.glOrientation.setOrientation(msg.roll, msg.pitch, msg.heading)
        self.emit(SIGNAL("redraw()"))
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Right:
            self.glOrientation.turnRight()
        elif key == Qt.Key_Left:
            self.glOrientation.turnLeft()
        self.glOrientation.updateGL()
        
    def createMainFrame(self):
        self.mainFrame = QWidget()
        
        self.glOrientation = GLOrientation()
        self.connect(self, SIGNAL('redraw()'), self.glOrientation.updateGL)
        vbox = QVBoxLayout()
        vbox.addWidget(self.glOrientation)

        self.mainFrame.setLayout(vbox)
        self.setCentralWidget(self.mainFrame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MarofGui()
    form.show()
    sys.exit(app.exec_())
