import pandas as pd
import numpy as np


max_bler = 0.05
meas_snr = 40

dfs = [pd.read_csv(f'mcs{mcs}_awgn_5G.csv', sep=';') for mcs in range(29)]
mcs_table = pd.concat(dfs)
mcs_table['bler'] = mcs_table.err0/mcs_table.trials0
row = mcs_table[(mcs_table.bler <= max_bler) & (mcs_table.SNR <= meas_snr)]
best_val = row.iloc[row.MCS.argmax()]
print(best_val.MCS, max_bler, best_val.bler, meas_snr, best_val.SNR)
