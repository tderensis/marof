import threading
import select
import atexit

import lcm

from marof_lcm import configModule_t

class MarofModuleHandler(object):
    """ Responsible for configuring a module through LCM. This includes starting and stopping. """
    
    def __init__(self, module):
        """ Module handler init """
        self._module = module
        
        self._lcm = lcm.LCM()
        self._lcm.subscribe("CONFIG", self._handleConfig)
        
        self._stopEvent = threading.Event() # to stop the handler thread
        
        # Create the handler thread, but don't start it yet
        self._handlerThread = threading.Thread(target=self._handlerMain)
        self._handlerThread.setDaemon(True) # A fail-safe to make things work with iPython
        
        # Close the thread upon Python exit
        atexit.register(self._release)
        
    def __del__(self):
        self._release()
        
    @property
    def module(self):
        """ The module property. """
        return self._module
    
    def _release(self):
        """ Stop the handling thread. """
        self._stopEvent.set()
        self._handlerThread.join()
        
    def subscribe(self, channel, function):
        """ Subscribe to a channel. """
        self._lcm.subscribe(channel, function)
        
    def start(self):
        """ Start the handler on another thread. All subscriptions need to be registered first. """
        self._handlerThread.start()
    
    def _handleConfig(self, channel, data):
        """ Handle a module configuration message. """
        print "Handing configuration message"
        config = configModule_t.decode(data)
        if config.name == self._module.name:
            # The message is for this module
            if config.command.equal('start'):
                self._module.start()
                print "Starting module", self._module.name
            elif config.command.equal('stop'):
                self._module.stop()
            
    def _handlerMain(self):
        """ Handle LCM messages until _stopEvent is set. """
        while not self._stopEvent.is_set():
            # wait until LCM has a message ready to read
            rc = select.select([self._lcm.fileno()], [], [self._lcm.fileno()], 0.05)
            if len(rc[0]) > 0 or len(rc[2]) > 0:
                self._lcm.handle()
    