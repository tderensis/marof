import threading
import select
import signal
import time
import lcm

from marof_lcm import config_t

class MarofModuleHandler(object):
    """ Responsible for configuring a module through LCM. This includes starting and stopping. 
    
    :param module: the MarofModule for which to handle messages.
    """
    
    def __init__(self, module):
        self._module = module
        
        self._lcm = lcm.LCM()
        self._lcm.subscribe("MODULE_CONFIG", self._handleModuleConfig)
        self._lcm.subscribe("HANDLER_CONFIG", self._handleHandlerConfig)
        
        self._moduleThread = threading.Thread(target=self._module.start)
        self._moduleThread.setDaemon(True)
        
        self._stopEvent = threading.Event() # to stop the handler thread
        signal.signal(signal.SIGINT, self._handleSigint) # Close the thread upon Python exit
        
    def __del__(self):
        self._release()
    
    def subscribe(self, channel, function):
        """ Subscribe to a channel. 
        
        :param channel: the channel string
        :param function: the function to subscribe to
        """
        self._lcm.subscribe(channel, function)
        
    def start(self):
        """ Start the handler on the current thread. This function will block until SIGINT or 
        a config message stops it. All subscriptions should to be registered first. 
        """
        self._run()
    
    def startModule(self):
        """ Start the module on another thread. """
        self._moduleThread.start()
        time.sleep(0.05) # Give the thread some time to start
    
    @property
    def module(self):
        """ The module property. """
        return self._module
    
    def _handleSigint(self, signal, frame):
        """ Handle the SIGINT signal. """
        self._release()
        
    def _release(self):
        """ Stop the module and handling thread. """
        self._module.stop()
        self._moduleThread.join()
        self._stopEvent.set()
    
    def _handleModuleConfig(self, channel, data):
        """ Handle a module configuration message. 
        
        :param channel: the channel string
        :param data: the data sent on the channel
        """
        config = config_t().decode(data)
        if config.name == self._module.name: # check if the message is for this module
            if config.command == 'start':
                if not self._module.isRunning:
                    self.startModule()
            elif config.command == 'stop':
                self._module.stop()
            elif config.command == 'pause':
                self._module.pause()
            elif config.command == 'resume':
                self._module.resume()
    
    def _handleHandlerConfig(self, channel, data):
        """ Handle a handler configuration message. 
        
        :param channel: the channel string
        :param data: the data sent on the channel
        """
        config = config_t().decode(data)
        if config.name == self._module.name:
            if config.command == 'stop':
                self._module.stop() # stop the module, or else there is no handler left to stop it
                self._stopEvent.set()
        
    def _run(self):
        """ Handle LCM messages until _stopEvent is set. """
        print "Starting handler for module", self._module.name
        while not self._stopEvent.is_set():
            # wait until LCM has a message ready to read
            try:
                rc = select.select([self._lcm.fileno()], [], [self._lcm.fileno()], 0.05)
            except select.error:
                continue # ignore the error
            if len(rc[0]) > 0 or len(rc[2]) > 0:
                self._lcm.handle()
        print "Stopped handler for module", self._module.name
