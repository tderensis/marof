import abc

class Filter(object):
    """ A filter for use with the Sensor class.
    """
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        return
    
    @abc.abstractmethod
    def step(self, currentInput):
        """ Perform the filter step using the given input.
        
        :param currentInput: the input to the filter step, could be a list
        :returns: the filter output with the same size as the input
        """
        return