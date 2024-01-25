import math
from numba import vectorize, float64
import numpy as np
import math
from scipy.constants import speed_of_light as c

@vectorize([float64(float64)])
def ETSI_pattern(alpha): 
    ''' well defined only for [-pi,+pi]'''
    return -min(12*((alpha)/np.radians(65))**2, 30)

@vectorize([float64(float64)])
def AEv(tetha):
    if tetha>math.pi*3/2:
        tetha=tetha-2*math.pi
    return ETSI_pattern(tetha-(math.pi/2))

@vectorize([float64(float64)])
def AEh(phi):
    if phi>math.pi:
        phi -= 2*math.pi
    return ETSI_pattern(phi)

@vectorize([float64(float64, float64)])
def AE(phi, theta):
    return 8-min(-(AEv(theta) + AEh(phi)), 30)

@vectorize([float64(float64,float64,float64,float64)])
def AA(tetha, phi, tetha_etilt, phi_escan):
    rho = 1
    Nh = 4
    Nv = 4
    v = np.array([[np.exp(1j*2*math.pi*(n*1/2 *np.cos(tetha) + m*1/2*np.sin(tetha)*np.sin(phi))) for m in range(Nh)] for n in range(Nv)])
    w = np.array([[np.exp(1j*2*math.pi*(n*1/2 *np.sin(tetha_etilt) - m*1/2*np.cos(tetha_etilt)*np.sin(phi_escan)))/np.sqrt(Nh*Nv) for m in range(Nh)] for n in range(Nv)])
    sum = np.abs(np.sum(np.multiply(v,w)))**2
    val = 10*np.log10(1+rho*(sum -1))+AE(phi, tetha)
    return val

