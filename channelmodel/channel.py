
import numpy as np
import math as m
# import numba
speed_of_light = 299792458


def snr(tx_power, tx_gain, rx_gain, pathloss,  bandwidth, NF):
    ''' Compute the Signal-to-Noise ratio
            Parameters:
            tx_power (float): Trasmission Power in dBm
            tx_gain (float): Transmission Gain in dB
            rx_gain (float): Reception Gain in dB
            pathloss (float): Pathloss of the channel in dBm
            bandwidth (float): Bandwidth of the transmission in MHz
            NF (float): Noise Figure of the receiver in dB
    '''
    return tx_power + tx_gain + rx_gain - pathloss - noise(bandwidth) - NF


def noise(bandwidth):
    '''Compute the thermic noise for a given bandwidth, assuming a noise density of -174dBm/Hz
            Parameters:
                bandwidth (float): Bandwidth of the transmission in MHz
            Returns
                noise (foat): Noise in dBm
    '''
    Nd = -174  # dBm/Hz
    noise = Nd + 10*np.log10(bandwidth*1e6)
    return noise


def pathloss_fspl(d, frequency):
    '''Compute the Free Space pathloss in dBm for a given distance and frequency
            Parameters:
                d (float): Distance in meters
                frequency (float): Carrier Frequency in GHz
            Returns:
                pathloss (float): Pathloss in dBm
    '''
    return 20*np.log10(d) + 20*np.log10(frequency*1e9) - 147.55

def get_indoor_pl(self, frequency):
    '''Compute the ETSI additional indoor pathloss in dBm from the TR 38.901 model O2I high loss model
            Parameters:
                frequency (float): Carrier Frequency in GHz
            Returns:
                pathloss (float): Pathloss in dBm
    '''
    #TR 38.901 model O2I high loss
    l_glass = 2+0.2*frequency
    l_concrete = 5+4*frequency
    loss = 5 - 10*m.log10(0.7*10**(-l_glass/10) + 0.3*10**(-l_concrete/10))
    return loss

# @numba.vectorize([numba.float64(numba.float64, numba.int32, numba.float64)])
def pathloss_etsi(d, los, frequency):
    '''Compute the ETSI pathloss in dBm for a given distance, frequency, and LoS state from the ETSI TR38.901 Channel Model
            Parameters:
                d (float): Distance in meters
                los (bool): Line of Sight state
                frequency (float): Carrier Frequency in GHz
            Returns:
                pathloss (float): Pathloss in dBm
    '''
    h_bs = 10
    h_ut = 1.5
    if d < 10:
        # Model is undefined for d<10
        d = 10
    breakpoint_distance = 2*np.pi*h_bs*h_ut*frequency*1e9/speed_of_light
    if d < breakpoint_distance:
        pl_los = 32.4 + 21*np.log10(d)+20*np.log10(frequency)  # + nrv_los.rvs(1)[0]
    else:
        pl_los = 32.4 + 40*np.log10(d)+20*np.log10(frequency) - 9.5*np.log10((breakpoint_distance)**2 + (h_bs-h_ut)**2)  # + nrv_los.rvs(1)[0]

    pl_nlos = 22.4 + 35.3*np.log10(d)+21.3*np.log10(frequency) - 0.3*(h_ut - 1.5)  # + nrv_nlos.rvs(1)[0]

    if los:
        pathloss = pl_los
    else:
        pathloss = max(pl_los, pl_nlos)
    return pathloss
