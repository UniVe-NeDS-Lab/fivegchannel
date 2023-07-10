### 5G  Channel Model Library

example:

```
import channelmodel.capacity as capacity
import channelmodel.channel as channel

#Init the tables
capacity.load_oai_tables()
capacity.load_3gpp_tables()

fc = 27 #GHz
B = 200 #Mhz 
NF = 7 #dBm
max_bler = 0.05 
tx_p = 30 #dBm
tx_g = rx_g = 18 #dB
num = 3
layers = 1

if fc <= 6:
    fr = 1
else:
    fr = 2

#Get etsi pathloss at 100m
pl_etsi = channel.pathloss_etsi(100.0, 1, fc)

#Get the SNR 
snr = channel.snr(tx_p, tx_g, rx_g, pl_etsi, B, NF)

#Compute the capacity
C =  capacity.capacity_snr(snr-1, B, max_bler, num, layers, fr)

print(C)
```
