
from numpy import bmat, mat, zeros
from scipy.linalg.matfuncs import expm

def zohe(A, B, T):
    """ Calculate the zero order hold equivalent of the continuous matrices A and
    B using a time step of T.
    
    :param A: continuous A matrix 
    :param B: continuous B matrix
    :param T: time step
    :returns: a tuple of discrete matrices (phi, gamma).
    """
    # Form the square matrix:  H = [ A  B ] * T
    #                              [ 0  0 ]
    zr = A.shape[1] + B.shape[1] - A.shape[0]
    H = bmat([[           A,                      B            ],
              [ zeros((zr,A.shape[1])), zeros((zr,B.shape[1])) ]]) * T
    # Calculate matrix exponential
    exp = expm(H)
    
    # Extract phi and gamma (discrete forms of A and B)
    phi = mat(exp[0:A.shape[0], 0:A.shape[1]])
    gamma = mat(exp[0:B.shape[0], A.shape[1]:exp.shape[1]])
    return (phi, gamma)


