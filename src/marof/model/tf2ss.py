
from marof.model import StateSpace
from numpy import mat, bmat, transpose, eye, zeros

def tf2ss(tf):
    #assert isinstance(tf, TF), "tf2ss() requires a transfer function"
    Ts = tf.Ts
    
    # Use observable canonical form
    n = len(tf.denominator) - 1
    a0 = tf.denominator[0]
    b0 = tf.numerator[0]
    num = [numerator/a0 for numerator in tf.numerator][1:] # chop off b0
    den = [denominator/a0 for denominator in tf.denominator][1:] # chop off a0
    
    aCol = transpose(mat([-a for a in den])) 
    bCol = []
    for i in range(0, n):
        bCol.append(num[i] - den[i]*b0)
        
    if n == 1:
        A = aCol
        C = 1
    else:
        A = bmat([[aCol, bmat([eye(n-1)], [zeros(1, n-1)])]])
        C = bmat([1, zeros(1, n-1)])
    B = transpose(mat(bCol))
    D = b0
    return StateSpace(A, B, C, D, Ts)
    