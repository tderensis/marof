import sys, signal
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import (QApplication, QMainWindow, QWidget, QLineEdit, QPushButton, QLabel, 
                         QFormLayout, QGridLayout, QVBoxLayout)
import lcm
from marof import getMicroSeconds
from marof_lcm import motorCommand_t

class SoftwareRC(QMainWindow):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Software RC')
        self._isKilled = True
        self._speed = 0.0
        self._turn = 0.0
        self._lcm = lcm.LCM()
        self.createMainFrame()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    def setAndSend(self):
        try:
            self._speed = float(str(self.speedPercentTextbox.text()).strip())
        except:
            self.speedPercentTextbox.setText(str(self._speed))
        self._speed = self.clampValue(self._speed)
        self.speedPercentTextbox.setText(str(self._speed))
        try:
            self._turn = float(str(self.turnPercentTextbox.text()).strip())
        except:
            self.turnPercentTextbox.setText(str(self._turn))
        self._turn = self.clampValue(self._turn)
        self.turnPercentTextbox.setText(str(self._turn))
        self.sendCommands()
            
    def sendCommands(self):
        msg = motorCommand_t()
        msg.time = getMicroSeconds()
        msg.speedPercent = self._speed
        msg.turnPercent = self._turn
        self._lcm.publish("MOTOR_COMMAND", msg.encode())
        
    def kill(self):
        msg = motorCommand_t()
        msg.time = getMicroSeconds()
        msg.speedPercent = 0
        msg.turnPercent = 0
        self._lcm.publish("MOTOR_COMMAND", msg.encode())
    
    def turnRight(self):
        self._turn += 10
        self._turn = self.clampValue(self._turn)
        self.turnPercentTextbox.setText(str(self._turn))
        self.sendCommands(self._speed, self._turn)
    
    def turnLeft(self):
        self._turn -= 10
        self._turn = self.clampValue(self._turn)
        self.turnPercentTextbox.setText(str(self._turn))
        self.sendCommands()
        
    def speedUp(self):
        self._speed += 10
        self._speed = self.clampValue(self._speed)
        self.speedPercentTextbox.setText(str(self._speed))
        self.sendCommands()
    
    def speedDown(self):
        self._speed -= 10
        self._speed = self.clampValue(self._speed)
        self.speedPercentTextbox.setText(str(self._speed))
        self.sendCommands()
    
    def clampValue(self, value, minVal=-100, maxVal=100):
        if value > maxVal:
            return maxVal
        elif value < minVal:
            return minVal
        return value
        
    def createMainFrame(self):
        self.mainFrame = QWidget()
        
        self.speedPercentTextbox = QLineEdit()
        self.speedPercentTextbox.setText(str(self._speed))
        self.speedPercentTextbox.setMinimumWidth(100)
        self.turnPercentTextbox = QLineEdit()
        self.turnPercentTextbox.setText(str(self._turn))
        self.turnPercentTextbox.setMinimumWidth(100)
        
        sendButton = QPushButton("Send")
        self.connect(sendButton, SIGNAL('clicked()'), self.setAndSend)
        killButton = QPushButton("Kill")
        self.connect(killButton, SIGNAL('clicked()'), self.kill)
        speedUpButton = QPushButton("^")
        self.connect(speedUpButton, SIGNAL('clicked()'), self.speedUp)
        speedDownButton = QPushButton("v")
        self.connect(speedDownButton, SIGNAL('clicked()'), self.speedDown)
        turnLeftButton = QPushButton("<")
        self.connect(turnLeftButton, SIGNAL('clicked()'), self.turnLeft)
        turnRightButton = QPushButton(">")
        self.connect(turnRightButton, SIGNAL('clicked()'), self.turnRight)
        
        speedLabel = QLabel('Speed Command')
        turnLabel = QLabel('Turn Command')
        
        formLayout = QFormLayout()
        formLayout.addRow(speedLabel, self.speedPercentTextbox)
        formLayout.addRow(turnLabel, self.turnPercentTextbox)
        
        grid = QGridLayout()
        grid.addWidget(speedUpButton, 1, 2)
        grid.addWidget(speedDownButton, 3, 2)
        grid.addWidget(turnLeftButton, 2, 1)
        grid.addWidget(turnRightButton, 2, 3)
        
        vbox = QVBoxLayout()
        vbox.addLayout(formLayout)
        vbox.addLayout(grid)
        vbox.addWidget(sendButton)
        vbox.addWidget(killButton)

        self.mainFrame.setLayout(vbox)
        self.setCentralWidget(self.mainFrame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = SoftwareRC()
    form.show()
    sys.exit(app.exec_())
