import abc
import time
from marof import MarofModule

class PidController(MarofModule):
    """ A simple PID controller. """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, updateInterval, kp, ki, kd):
        """ Initialize the controller """
        super(PidController, self).__init__(name, updateInterval)
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._lastError = 0
        self._errorSum = 0
        self._lastUpdateTime = None
        self._command = None
    
    @property
    def kp(self):
        return self._kp
    
    @kp.setter
    def kp(self, kp):
        self._kp = kp
        
    @property
    def ki(self):
        return self._ki
    
    @ki.setter
    def ki(self, ki):
        self._ki = ki
        
    @property
    def kd(self):
        return self._kd
    
    @kd.setter
    def kd(self, kd):
        self._kd = kd
        
    @abc.abstractproperty
    def currentState(self):
        return self._currentState
    
    @currentState.setter
    def currentState(self, state):
        self._currentState = state
    
    @abc.abstractproperty
    def desiredState(self):
        return self._desiredState
    
    @desiredState.setter
    def desiredState(self, state):
        self._desiredState = state
        
    @abc.abstractmethod
    def stateDifference(self, desired, current):
        """ Gets the difference between states """
        return
    
    @property
    def nextCommand(self):
        """ The last command calculated in the step function. """
        return self._command
    
    def step(self):
        current = self.currentState
        desired = self.desiredState
        
        currentTime = time.time()
        if self._lastUpdateTime == None:
            deltaT = 0.1
        else:
            deltaT = currentTime - self._lastUpdateTime
        
        # P Error
        error = self.stateDifference(desired, current)
        # I Error
        self._errorSum += (error * deltaT);
        # D Error
        errorDiff = self.stateDifference(self._lastHeadingError, error)/deltaT

        # Compute the turning command
        self._command = -(error * self._kp + 
                    self._headingErrorSum *self._ki +
                    errorDiff * self.kd)
        
        self._lastError = error
        self._lastUpdateTime = currentTime
        