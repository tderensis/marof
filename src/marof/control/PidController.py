import abc
from marof import MarofModule

class PidController(MarofModule):
    """ A simple PID controller. """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, updateInterval, kp, ki, kd):
        """ Initialize the controller """
        super(PidController, self).__init__(name, updateInterval)
        self._kp = kp
        self._ki = ki * updateInterval # update interval is represented in ki and kd gains
        self._kd = kd / updateInterval
        self._currentState = 0
        self._desiredState = 0
        self._lastInput = 0
        self._errorSum = 0
        self._output = 0
        self._minOutput = -100
        self._maxOutput = 100
    
    def setGains(self, kp, ki, kd):
        self._kp = kp
        self._ki = ki * self.updateInterval
        self._kd = kd / self.updateInterval
        
    @property
    def currentState(self):
        return self._currentState
    
    @currentState.setter
    def currentState(self, state):
        self._currentState = state
    
    @property
    def desiredState(self):
        return self._desiredState
    
    @desiredState.setter
    def desiredState(self, state):
        self._desiredState = state
    
    @property
    def minOutput(self):
        return self._minOutput
    
    @property
    def maxOutput(self):
        return self._maxOutput
    
    def setLimits(self, minOut, maxOut):
        assert minOut < maxOut, "min must be less than max"
        self._minOutput = minOut
        self._maxOutput = maxOut
        
        self._output = self._clampValue(self._output, minOut, maxOut)
        self._errorSum = self._clampValue(self._errorSum, minOut, maxOut) 
            
    def _clampValue(self, value, minValue, maxValue):
        """ Ensure the given value is within the given range. """
        if value > maxValue: 
            return maxValue
        elif value < minValue: 
            return minValue
        return value
    
    @abc.abstractmethod
    def stateDifference(self, desired, current):
        """ Gets the difference between states """
        return
    
    @property
    def output(self):
        """ The last command calculated in the step function. """
        return self._output
    
    def step(self):
        if self._isPaused: return
        current = self._currentState
        desired = self._desiredState
        
        # P Error
        error = self.stateDifference(desired, current)
        # I Error - Multiply gain here to prevent jump when changing PID constants.
        self._errorSum += (self._ki * error)
        self._errorSum = self._clampValue(self._errorSum, self._minOutput, self._maxOutput) # prevent windup
        # D Error - Use input difference to remove derivative kick.
        errorDiff = self.stateDifference(current, self._lastInput)

        # Compute the next command
        self._output = (error * self._kp +      # P
                        self._errorSum -        # I
                        errorDiff * self._kd)   # D
        self._output = self._clampValue(self._output, self._minOutput, self._maxOutput)
        #print "error:", error, "errorSum:", self._errorSum, "errorDiff", errorDiff
        self._lastInput = current
