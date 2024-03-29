import pandas as pd
import numpy as np
import os

this_folder = os.path.dirname(__file__)


def load_oai_tables():
    '''Load in memory the tables with the MCS BLER SNR values
    '''
    dfs = [pd.read_csv(f'{this_folder}/sinr_bler/OAI/SISO/mcs{mcs}_awgn_5G.csv', sep=';') for mcs in range(29)]
    global mcs_table_siso
    mcs_table_siso = pd.concat(dfs)
    mcs_table_siso['bler'] = mcs_table_siso.err0/mcs_table_siso.trials0
    dfs = [pd.read_csv(f'{this_folder}/sinr_bler/OAI/MIMO/mcs{mcs}_cdlc_mimo2x2_dl.csv', sep=';') for mcs in range(29)]
    global mcs_table_mimo
    mcs_table_mimo = pd.concat(dfs)
    mcs_table_mimo['bler'] = mcs_table_mimo.err0/mcs_table_mimo.trials0

    return


def load_3gpp_tables(direction='dl', table=1) -> None:
    '''Load in memory the tables with the 3gpp DLSCH tables
            Parameters:
                direction (str): In what direction (dl for DLSCH, ul for ULSCH)
                table (int): What table to load [1,2,3]
    '''
    if table == 1 and direction == 'dl':
        filename = 'PDSCH_table1.csv'
    elif table == 2 and direction == 'dl':
        filename = 'PDSCH_table2.csv'
    else:
        raise Exception("Table not found")
    global table_3gpp
    table_3gpp = pd.read_csv(f'{this_folder}/{filename}', delimiter=',', index_col='mcs')
    return


# def mcs_shannon(snr):
#     meas_se = m.log2(1 + 10**(snr/10))
#     row = table_3gpp[table_3gpp.se > meas_se]
#     for mcs, se in enumerate(se_table):
#         if meas_se < se:
#             break
#     return mcs-1


def mcs(meas_snr: float, max_bler: float, layers: int) -> int:
    ''' Compute the usable MCS for a given SNR using the OpenAirInterface tables
            Parameters:
                meas_snr (float): SNR measured from the RX device
                max_bler (float): Maximum Block Error Rate
                layers (int): MIMO layers [1,2,4,8]
            Returns:
                mcs (int): Maximum usable MCS
    '''
    if layers == 1:
        row = mcs_table_siso[(mcs_table_siso.bler <= max_bler) & (mcs_table_siso.SNR <= meas_snr)]
    else:
        row = mcs_table_mimo[(mcs_table_mimo.bler <= max_bler) & (mcs_table_mimo.SNR <= meas_snr)]
    if not row.empty:
        best_val = row.iloc[row.MCS.argmax()]
        # print(best_val.MCS, max_bler, best_val.bler, meas_snr, best_val.SNR)
        return int(best_val.MCS)
    else:
        return -1


def modord_rate(mcs: int, table: int, direction: str = 'dl') -> tuple[float, float]:
    ''' Retrieve the code rate and the  modulation order for a given MSC from the tables stored in the csv files.
            Parameters:
                mcs (int): Modulation and Coding Scheme
                direction (str): Data link direction ['ul', 'dl']
                table (int): Which table to look into
            Returns: 
                (modord, rate): A tuple with the modulation order and coderate
    '''
    if table == 1 and direction == 'dl':
        filename = 'PDSCH_table1.csv'
    elif table == 2 and direction == 'dl':
        filename = 'PDSCH_table2.csv'
    else:
        raise Exception("Table not found")
    row = table_3gpp.loc[mcs].values
    return (row[0], row[1])


def capacity(mcs: int, prb: int, layers: int, num: int, fr: int, slot_r: float = 0.7, direction: str = 'dl', table=1) -> float:
    '''Compute the capacity of a 5G channel using the formula taken from 3GPP TS 38.306.
            Parameters:
                mcs (int): The modulation and coding scheme used
                prb (int): Numbers of resource blocks
                layers (int): Number of MIMO layers
                num (int): Numerology [0,1,2,3]
                fr (int): Frequency Range [1,2]
                slot_r (float): Ratio of Uplink to Downlink slots 
                direction (str): Data link direction ['ul', 'dl']
                table (int): Which MSC table to use [1,2,3] from TS 38.214

            Returns:
                C (float): Capacity in Mb/s
    '''
    Tus = (10**-3)/(14*2**num)
    if direction == 'ul':
        raise Exception("Not yet implemented")
        # coderate table is different for PUCCH
        if fr == 1:
            OH = 0.08
        elif fr == 2:
            OH = 0.10
        else:
            raise Exception("Wrong FR")
        ratio = 1-slot_r
    elif direction == 'dl':
        if fr == 1:
            OH = 0.14
        elif fr == 2:
            OH = 0.18
        else:
            raise Exception("Wrong FR")
        ratio = slot_r
    else:
        raise Exception("Wrong direction")
    mod_ord, code_rate = modord_rate(mcs, table)
    C = 1e-6*layers*mod_ord*code_rate/1024*prb*12/Tus*(1-OH)*ratio
    return C


def get_resource_blocks(bandwidth: int, num: int, fr: int) -> int:
    '''Get the number of resource blocks corresponding to a given bandwidth and numerology
            Parameters:
                bandwidth (int): bandwidth of the transmission in MHz
                num (int): numerology [0,1,2,3]
                fr (int): frequency range 1 for FR1, 2 for FR2
            Returns:
                prb (int): number of resource blocks 
    '''
    num_scs = [15, 30, 60, 120]
    scs_bandwidth_dict_fr1 = {15: {5: 25, 10: 52, 15: 79, 20: 106, 25: 133, 30: 160, 35: 188, 40: 216, 45: 242, 50: 270},
                              30: {5: 11, 10: 24, 15: 38, 20: 51, 25: 65, 30: 78, 35: 92, 40: 106, 45: 119, 50: 133, 60: 162, 70: 189, 80: 217, 90: 245, 100: 273},
                              60: {10: 11, 15: 18, 20: 24, 25: 31, 30: 38, 35: 44, 40: 51, 45: 58, 50: 65, 60: 79, 70: 93, 80: 107, 90: 121, 100: 135},
                              }

    scs_bandwidth_dict_fr2 = {60: {50: 66, 100: 132, 200: 264},
                              120: {50: 32, 100: 66, 200: 132, 400: 264}}

    scs = num_scs[num]
    if fr == 1:
        prb = scs_bandwidth_dict_fr1[scs][bandwidth]
    elif fr == 2:
        prb = scs_bandwidth_dict_fr2[scs][bandwidth]
    else:
        raise Exception("Wrong FR")

    return prb


def capacity_snr(snr: float, bandwidth: int, max_bler: float, num: int, layers: int, fr: int):
    '''Compute the capacity of a 5G channel given the SNR using the formula taken from 3GPP TS 38.306.
            Parameters:
                snr (float): Signal to noise ratio in dBm
                bandwidth (int): Bandwidth
                max_bler (float): Maximum block error rate
                num (int): Numerology [0,1,2,3]
                layers (int): Number of MIMO layers
                fr (int): Frequency Range [1,2]
            Returns:
                C (float): Capacity in Mb/s
    '''
    prb = get_resource_blocks(bandwidth, num, fr)
    i = mcs(snr, max_bler, layers)
    if i >= 0:
        C = capacity(i, prb, layers, num, fr, table=1)
    else:
        C = 0
    return C


def shannon(snr: float, bandwidth: int, layers: int):
    '''Compute the capacity of a 5G channel given the SNR using Shannon Model.
            Parameters:
                snr (float): Signal to noise ratio in dBm
                bandwidth (int): Bandwidth    
                layers (int): Number of MIMO layers
            Returns:
                C (float): Capacity in Mb/s
    '''
    lin_snr = 10**(snr/10)
    C = layers*bandwidth*1e6*np.log2(1+lin_snr) * 10**-6  # to get Mbps
    return C
