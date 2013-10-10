import abc

class Filter(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        """ Initialization for filters. """
        return
    
    @abc.abstractmethod
    def step(self, currentInput):
        """ Perform the filter step using the given input. """
        return