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

    def publishUpdate(self):
        return
    
    def step(self):
        return        
    
    def sendCommand(self, speedPercent, turnPercent):
        speedPercent = self.limitPercent(speedPercent)
        turnPercent = self.limitPercent(turnPercent)
        
        rightPercent = self.limitPercent(speedPercent-turnPercent) # right turn is positive
        leftPercent = self.limitPercent(speedPercent+turnPercent)
        rightDir = GPIO.LOW
        leftDir = GPIO.LOW
        if rightPercent < 0:
            rightDir = GPIO.HIGH
        if leftPercent < 0:
            leftDir = GPIO.HIGH
        print rightDir, rightPercent, leftDir, leftPercent
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
    dagu = DaguRover("DAGU_CONTROL", 0.1, "P9_21", "P9_11", "P9_22", "P9_12")
    handler = MarofModuleHandler(dagu)
    handler.subscribe("MOTOR_COMMAND", dagu.handleMotorCommand)
    handler.startModule()
    handler.start()
