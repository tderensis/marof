from math import fabs
from marof import MarofModule
from marof_lcm import motorCommand_t

import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.GPIO as GPIO

class DaguRover(MarofModule):
    """ Class to send commands to the motor controller. """
    def __init__(self, name, updateInterval, pwmRight, dirRight, pwmLeft, dirLeft):
        super(DaguRover, self).__init__(name, updateInterval)
        self._pwmRight = pwmRight
        self._dirRight = dirRight
        self._pwmLeft = pwmLeft
        self._dirLeft = dirLeft
        
        PWM.start(self._pwmRight, 0)
        GPIO.setup(self._dirRight, GPIO.OUT)
        GPIO.output(self._dirRight, GPIO.LOW)
        PWM.start(self._pwmLeft, 0)
        GPIO.setup(self._dirLeft, GPIO.OUT)
        GPIO.output(self._dirLeft, GPIO.LOW)
        
    def __del__(self):
        PWM.stop(self._pwmRight)
        PWM.stop(self._pwmLeft)
        
    def sendCommand(self, speedPercent, turnPercent):
        speedPercent = self.limitPercent(speedPercent)
        turnPercent = self.limitPercent(turnPercent)
        
        rightPercent = self.limitPercent(speedPercent-turnPercent) # right turn is positive
        leftPercent = self.limitPercent(speedPercent+turnPercent)
        rightDir = GPIO.HIGH
        leftDir = GPIO.HIGH
        if rightPercent < 0:
            rightDir = GPIO.LOW
        if leftPercent < 0:
            leftDir = GPIO.LOW
        
        GPIO.output(self._dirRight, rightDir)
        GPIO.output(self._dirLeft, leftDir)
        PWM.set_duty_cycle(self._pwmRight, fabs(rightPercent))
        PWM.set_duty_cycle(self._pwmLeft, fabs(leftPercent))
        
    def handleMotorCommand(self, channel, msg):
        motorCommand = motorCommand_t.decode(msg)
        self.sendCommand(motorCommand.speedPercent, motorCommand.turnPercent)
        
    def limitPercent(self, percent):
        """ Limit the percent to between -100 and 100. """
        if percent > 100:
            return 100
        elif percent < -100:
            return -100
        else:
            return percent

        
from marof import MarofModuleHandler
    
if __name__ == "__main__":
    dagu = DaguRover("DAGU_CONTROL", 0.1, "P9_14", "P9_15", "P9_16", "P9_17")
    handler = MarofModuleHandler(dagu)
    handler.subscribe("MOTOR", dagu.handleMotorCommand)
    handler.start()
    dagu.start()
    