# this is where functions are defined to read the phase and to change the tuning voltage

import pyvisa
import time

# COM ports of power source and phase detector
POW_COM = 3
PH_COM = 4

rm = pyvisa.ResourceManager()

# set up power supply
pow = rm.open_resource('ASRL' + str(POW_COM) + '::INSTR')
pow.read_termination = '\r\n'
# remote operation mode
pow.write('syst:rem')
# set overvoltage protection
pow.write('volt:prot 5')
# set initial output voltage to 0
pow.write('volt 0')
# turn on the output
pow.write('outp on')
# close the connection
pow.close()

# set up phase detector
ph = rm.open_resource('ASRL' + str(PH_COM) + '::INSTR')

# function to set tuning voltage on power supply
def tune(v):
    # open the connection
    pow.open()

    # tuning voltage should range 0 to 5
    if v < 0:
        v = 0
    elif v > 5:
        v = 5

    # set new tuning voltage
    pow.write('volt ' + str(v))
    # close the connection
    pow.close()

# function to read phase difference between ULN and reference
def phase():
    # clear all of the measurements it has done since the last one
    ph.clear()
    # read phase string
    p = ph.read()
    # cut out non-numeric characters
    p = p.strip()[:-3].strip()

    # in case it got a bad reading, keep trying until it succeeds
    while p == '':
        p = ph.read().strip()[:-3].strip()

    # convert to -180 - 180 deg range and round
    p = round((float(p) + 180) % 360 - 180, 1)
    
    return p


if __name__ == "__main__":
    tune(0)
    prev_t = time.time()
    for i in range(30):
        print(phase())
        now = time.time()
        print(now - prev_t)
        prev_t = now