import abc
from marof import MarofModule

class Sensor(MarofModule):
    """ A sensor module. Has an optional filter. """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, name, updateInterval, filt):
        """ Initialize sensor. """
        super(Sensor, self).__init__(name, updateInterval)
        self._filter = filt
        self._filterOutput = None
        
    @property
    def filter(self):
        return self._filter
    
    @property
    def filterOutput(self):
        """ The output of the filter. """
        return self._filterOutput
    
    @abc.abstractproperty
    def filterInput(self):
        """ The input to the filter. """
        return
    
    @abc.abstractmethod
    def sensorStep(self):
        """ Where the sensor does all of its work. """
        return
    
    def step(self):
        self.sensorStep()
        if self._filter is not None:
            self._filterOutput = self._filter.step(self.filterInput)
    
    
    