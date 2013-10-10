import abc
from marof import MarofModule

class Sensor(MarofModule):
    """ A sensor module. Has an optional filter. """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, updateInterval, filt):
        """ Initialize sensor. """
        super(Sensor, self).__init__(name, updateInterval)
        self._filter = filt
        
    @property
    def filter(self):
        return self._filter
    
    def step(self):
        self.sensorStep()
        self.applyFilter()
    
    @abc.abstractmethod
    def applyFilter(self):
        """ A sensor must implement its filter. """
        return
    
    @abc.abstractmethod
    def sensorStep(self):
        """ Where the sensor does all of its work. """
        return
    