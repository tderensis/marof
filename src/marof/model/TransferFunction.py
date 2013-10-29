
class TransferFunction(object):
    r""" A transfer function.
    
    ..  math::
        H(s) = \frac{Y(s)}{X(s)} = 
        \frac{b_0 s^n + b_1 s^{n-1} + \ldots + b_n}{a_0 s^n + a_1 s^{n-1} + \ldots + a_n}
    
    ..  todo: Implement MIMO systems
    """
    def __init__(self, num, den, Ts = 0):
        assert Ts >= 0, "Sampling interval needs to be greater (discrete) or equal to 0 (continuous)"
        if Ts == 0: 
            self._discrete = False
        elif Ts > 0: 
            self._discrete = True
        
        self._numerator = num
        self._denominator = den
        self._Ts = Ts
    
    @property
    def numerator(self):
        return self._numerator
    
    @numerator.setter
    def numerator(self, numerator):
        self._numerator = numerator
        
    @property
    def denominator(self):
        return self._denominator
    
    @denominator.setter
    def denominator(self, denominator):
        self._denominator = denominator
        
    @property
    def Ts(self):
        return self._Ts
       
    def __str__(self):
        """ Print the transfer function """
        s = str(self._numerator)
        return s