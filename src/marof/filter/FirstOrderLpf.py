from math import pi
from marof.filter import Filter

class FirstOrderLpf(Filter):
    r""" A first-order low-pass filter with the Laplace transform:
    
    ..  math::
        \frac{\text{Output}}{\text{Input}} = \frac{K}{1 + s\tau}
        
    where :math:`K` is the passband gain and :math:`\tau` is the filter time constant which can
    be related to the cutoff frequency :math:`f_c` in hertz at -3 dB.
    
    ..  math::
        \tau = \frac{1}{2 \pi f_c}
        
    This can be converted to discrete time using the sampling interval :math:`T_s` and defining
    the variable :math:`\alpha` which is called the smoothing factor.
    
    ..  math:: 
        y[k] = \alpha y[k-1] + (1-\alpha) x[k]
    ..  math::
        \alpha = \frac{T_s}{T_s + \tau} \qquad \text{where} \qquad 0 \le \alpha \le 1
        
    This implementation is an exponentially-weighted moving average. Notice that a smoothing factor
    close to one will smooth the output less and a smoothing factor close to zero will cause the 
    output to respond to change in input slowly, giving the system more inertia.
    
    :param cutoff: default 1 Hz, the cutoff frequency in Hz
    :param samplingInterval: default 0.1 sec, the sampling interval in seconds
    :param gain: default 1, the gain of the filter
    
    ..  todo:: Implement multiple inputs, maybe with numpy, lists, or tuples
    """
    
    def __init__(self, cutoff=1, samplingInterval=0.1, gain=1):
        assert cutoff > 0, 'cutoff frequency is negative or 0'
        assert samplingInterval > 0, 'sampling interval is negative or 0'
        assert gain > 0, 'gain is negative or 0'
        
        timeConstant = 1.0/(2.0*pi*cutoff)
        self._a = samplingInterval/(samplingInterval + timeConstant)
        self._gain = gain
        self._lastOutput = None
        
    def step(self, currentInput):
        if self._lastOutput == None:
            self._lastOutput = currentInput
        self._lastOutput = self._gain*(self._a * currentInput + (1.0 - self._a) * self._lastOutput)
        return self._lastOutput
    
