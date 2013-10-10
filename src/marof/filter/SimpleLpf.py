from marof.filter import Filter

class SimpleLpf(Filter):
    """ A discrete first-order low-pass filter of the form:
    
    .. math:: y[k] = a y[k-1] + (1-a) x[k] \\
    where x[k] is the current filter input \\
    y[k] is the filter output \\
    y[k-1] is the last filter output \\
    a is the filter constant 0 <= a < 1
    
    Laplace: 1/(1 + s/w_c)
    w_c = cutoff (2pi * frequency in Hz)
    a = 1/(1 + Ts*w_c) where Ts is the sampling interval
    
    """
    
    def __init__(self, filterConstant):
        """ Initialization for the LPF. """
        if filterConstant < 0 or filterConstant >= 1:
            raise Exception("A simple LPF requires a filter constant 0 <= a < 1")
        self._a = filterConstant
        self._lastOutput = None
    
        
    def step(self, currentInput):
        if self._lastOutput == None:
            self._lastOutput = currentInput
        self._lastOutput = self._a*self._lastOutput + (1.0-self._a)*currentInput
        return self._lastOutput