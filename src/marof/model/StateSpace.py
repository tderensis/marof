from numpy import matrix

class StateSpace(object):
    r""" A simple class to hold a state space model of the form:
    
    ..  math::
        \dot{\bm{x}}(t) &= \bm{A}\bm{x}(t) + \bm{B}\bm{u}(t) \\
        \bm{y}(t) &= \bm{C}\bm{x}(t) + \bm{D}\bm{u}(t)
        
    Or if sampling interval T is specified:
    
    ..  math::
        \bm{x}[k+1] &= \bm{A}\bm{x}[k] + \bm{B}\bm{u}[k] \\
        \bm{y}[k] &= \bm{C}\bm{x}[k] + \bm{D}\bm{u}[k]
        
    :param A: the A matrix
    :param B: the B matrix
    :param C: the C matrix
    :param D: the D matrix
    :param Ts: default 0, the sampling interval
    """
    def __init__(self, A, B, C, D, Ts = 0):
        assert Ts >= 0, "Sampling interval needs to be greater (discrete) or equal to 0 (continuous)"
        if Ts == 0: 
            self._discrete = False
        elif Ts > 0: 
            self._discrete = True
        self._A = matrix(A)
        self._B = matrix(B)
        self._C = matrix(C)  
        self._D = matrix(D)
        self._Ts = Ts;
       
    def __str__(self):
        """ Print the matrix nice """
        s =  str(self.A) + " = A \n\n" + str(self.B) + " = B \n\n"
        s += str(self.C) + " = C \n\n" + str(self.D) + " = D \n"
        s += "discrete:" + str(self._discrete)
        return s
    
    @property
    def A(self):
        return self._A
    
    @A.setter
    def A(self, A):
        self._A = matrix(A)
        
    @property
    def B(self):
        return self._B
    
    @B.setter
    def B(self, B):
        self._B = matrix(B)
    
    @property
    def C(self):
        return self._C
    
    @C.setter
    def C(self, C):
        self._C = matrix(C)
        
    @property
    def D(self):
        return self._D
    
    @D.setter
    def D(self, D):
        self._D = matrix(D)
    
    @property
    def Ts(self):
        return self._Ts
    
    @property
    def discrete(self):
        return self._discrete


def stepSS(self, ss, x, u):
    """ Uses the current state x and input u to step the model to the next state 
    assuming the model is discrete. Assumes this method is called every T 
    seconds if it is run in real time.
    Outputs the next state and output (x, y).
    """
    if ss.discrete:
        x1 = ss.A * x + ss.B * u
        y = ss.C * x1 + ss.D * u
        return (x1, y)
    else:
        raise "Cannot step a continuous state space model"
