from math import pi
from marof.filter import Filter

class FirstOrderHpf(Filter):
    r""" A first-order high-pass filter with the Laplace transform:
    
    ..  math::
        \frac{\text{Output}}{\text{Input}} = \frac{K s \tau}{1 + s \tau}
        
    where :math:`K` is the passband gain and :math:`\tau` is the filter time constant which can
    be related to the cutoff frequency :math:`f_c` in hertz at -3 dB.
    
    ..  math::
        \tau = \frac{1}{2 \pi f_c}
        
    This can be converted to discrete time using the sampling interval :math:`T_s` and defining
    the variable :math:`\alpha`.
    
    ..  math:: 
        y[k] = \alpha y[k-1] + \alpha (x[k] - x[k-1])
    ..  math::
        \alpha = \frac{\tau}{\tau + T_s} \qquad \text{where} \qquad 0 \le \alpha \le 1
    
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
        self._a = timeConstant/(samplingInterval + timeConstant)
        self._gain = gain
        self._lastOutput = None
        self._lastInput = None
        
    def step(self, currentInput):
        if self._lastOutput is None:
            self._lastOutput = currentInput
        if self._lastInput is None:
            self._lastInput = currentInput
        self._lastOutput = self._gain*(self._a * (self._lastOutput + currentInput - self._lastOutput))
        self._lastInput = currentInput
        return self._lastOutput
    
