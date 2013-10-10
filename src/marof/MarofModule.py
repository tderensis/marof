import abc
import time
import lcm

from timing import getSeconds

class MarofModule(object):
    """ Parent class of all MARoF modules. 
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, updateInterval):
        """ Initialize the module """
        self._name = name
        if updateInterval < 0:
            raise Exception("Update Interval cannot be negative")
        self._updateInterval = updateInterval
        self._lcm = lcm.LCM()
        #self._publishInterval = 0.1
        self._isRunning = False
        self._isPaused = False
    
    @property
    def name(self):
        """ Every module has a name """
        return self._name
    
    @property
    def updateInterval(self):
        """ The update interval in seconds. """
        return self._updateInterval
    
    @property
    def lcmTX(self):
        """ The lcm object used to transmit."""
        return self._lcm
    
    def start(self):
        """ Start the module. This method blocks till the module is done or is stopped by the
        handler. Should be called last after handler is started. """
        print "Starting module:", self.name
        self._isRunning = True
        self._isPaused = False
        self.run()
    
    def stop(self):
        """ Stop the running module and exit. Assumes the module is well behaved and finishes
        the current step. """
        self._isRunning = False
    
    def pause(self):
        """ Pause the module. Stops publishing messages and calculations done in the step method """
        self._isPaused = True
    
    def resume(self):
        """ Resume the module after pause. """
        self._isPaused = False
                
    def run(self):
        """ Run the module. Calls the step method. """
        while self._isRunning:
            delta = getSeconds()
            if self._isPaused == False:
                self.step()
                self.publishUpdate()
            delta = getSeconds() - delta
            
            if self._updateInterval == 0:
                continue
            elif delta < self._updateInterval:
                time.sleep(self._updateInterval - delta)
            else:
                print "Warning: Module ", self._name, " took too long between steps"
    
    def publish(self, channel, lcmMsg):
        """ Publish a message. """
        self._lcm.publish(channel, lcmMsg.encode())
        
    @abc.abstractmethod
    def publishUpdate(self):
        """ Publish any messages over LCM. """
        return
        
    @abc.abstractmethod
    def step(self):
        """ The module's main function that does the actual module task. Returns the message
        to publish. """
        return
    
        