import abc
import traceback
import sys
import time

class MarofModule(object):
    """ Parent class of all MARoF modules. Thread safe
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, updateInterval):
        """ Initialize the module """
        self._name = name
        self._updateInterval = updateInterval
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
        try:
            while self._isRunning:
                delta = time.time()
                if self._isPaused == False:
                    self.step()
                    self.publishUpdate()
                delta = time.time() - delta
                
                if delta < self._updateInterval:
                    time.sleep(self._updateInterval - delta)
                else:
                    print "Warning: Module ", self._name, " took too long between steps"
        except Exception as e:
            print e.__str__()
            print str(sys.exc_info()[0])
            print traceback.format_exc()
    
    @abc.abstractmethod
    def step(self):
        """ The module's main function that does the actual module task. """
        return
    
    @abc.abstractmethod
    def publishUpdate(self):
        """ Publish the next update """
        return
    
        