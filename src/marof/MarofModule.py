import abc
from time import time, sleep
import threading
import signal
import Queue

import lcm

class MarofModule(object):
    """ Parent class of all MARoF modules.
    
    :param name: The name string of the module. Should be unique.
    :param updateInterval: the interval to update the module in seconds
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, updateInterval):
        """ Initialize the module """
        assert updateInterval >= 0, 'Update interval is negative'
        self._name = name
        self._updateInterval = updateInterval
        self._lcm = lcm.LCM()
        self._stopEvent = threading.Event()
        self._isRunning = False
        self._isPaused = False
        self._modQueue = Queue.Queue() # queue for commands that modify the module
        signal.signal(signal.SIGINT, self._handleSigint)
    
    def start(self):
        """ Start the module. This method blocks till the module is done or is stopped by the
        handler. Should be called last after handler is started. """
        self._isRunning = True
        self._isPaused = False
        self._run()
    
    def stop(self):
        """ Stop the running module and exit. Assumes the module is well behaved and finishes
        the current step. """
        self._isRunning = False
    
    def pause(self):
        """ Pause the module. Stops the step() and publishUpdate() methods. The module is still
        updated by the runLater() method. """
        self._isPaused = True
    
    def resume(self):
        """ Resume the module after pause. """
        self._isPaused = False
    
    def publish(self, channel, lcmMsg):
        """ Publish a message on the given channel. 
        
        :param channel: the channel string
        :param lcmMsg: the LCM message to publish
        """
        self._lcm.publish(channel, lcmMsg.encode())
    
    def runLater(self, command):
        """ Add a command to be run after the current step and publish method. This is for thread
        safety while handling asynchronous messages. 
        
        :param command: the command string to be evaluated later
        """
        self._modQueue.put(command)
    
    def _run(self):
        """ Run the module. Calls the step method. This method blocks. """
        print "Starting module", self._name, "with update interval:", self._updateInterval
        while self._isRunning:
            delta = time()
            
            if not self._isPaused:
                self.step()
                self.publishUpdate()
            
            # Run commands outside the step and publish methods to modify the module safely
            while not self._modQueue.empty():
                exec(self._modQueue.get())
                
            if self._updateInterval == 0:
                continue
            
            delta = self._updateInterval + delta - time()
            if delta > 0:
                sleep(delta)
            else:
                print "Warning: Module", self._name, " took too long between steps"
                
        print "\nStopped module", self._name
    
    def _handleSigint(self, signal, frame):
        self.stop()
        
    @property
    def isRunning(self):
        return self._isRunning
    
    @property
    def isPaused(self):
        return self._isPaused
    
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
    
    @abc.abstractmethod
    def publishUpdate(self):
        """ Publish any messages over LCM. """
        return
        
    @abc.abstractmethod
    def step(self):
        """ The module's main function that does the actual module task. """
        return
    