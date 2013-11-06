from math import fabs, copysign
from PidController import PidController
from marof_lcm import motorCommand_t, desiredState_t, currentState_t
from marof import MarofModuleHandler
from marof import getMicroSeconds

class HeadingPid(PidController):
    """ A heading PID controller """
    
    def __init__(self, name, updateInterval, kp, ki, kd, forwardSpeed):
        super(HeadingPid, self).__init__(name, updateInterval, kp, ki, kd)
        self.setLimits(-100, 100)
        self._forwardSpeed = forwardSpeed
    
    def stateDifference(self, desired, current):
        diff = (desired - current) % 360
        mag = fabs(diff)
        if mag > 180:
            east = mag-360
            diff = copysign(east, -diff)
        return diff
    
    def publishUpdate(self):
        msg = motorCommand_t()
        msg.time = getMicroSeconds()
        msg.speedPercent = self._forwardSpeed
        msg.turnPercent = self.output
        self.publish(self.name, msg)
        
    def desiredHandler(self, channel, encoded):
        msg = desiredState_t().decode(encoded)
        if msg.waypointMode == 0:
            self.runLater("self.desiredState =" + str(msg.heading))
    
    def currentHandler(self, channel, encoded):
        msg = currentState_t().decode(encoded)
        self.currentState = msg.heading

if __name__=="__main__":
    speed = 50
    T = 0.1
    pid = HeadingPid("Heading_PID", T, 5, 0.1, 3, speed)
    handler = MarofModuleHandler(pid)
    handler.subscribe("DESIRED_STATE", pid.desiredHandler)
    handler.subscribe("CURRENT_STATE", pid.currentHandler)
    handler.startModule()
    handler.start()
