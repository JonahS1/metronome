# this is where functions are defined to read the phase and to change the tuning voltage

import pyvisa
import time

# resource strings of power source and phase detector
POW_RESOURCE = 'ASRL3::INSTR'
PH_RESOURCE = 'ASRL4::INSTR'

rm = pyvisa.ResourceManager('@py')

# set up power supply
pow = rm.open_resource(POW_RESOURCE)
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
ph = rm.open_resource(PH_RESOURCE)

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
    ph.flush(1)
    # read phase and remove all '\x00's from the beginning
    p = ph.read()
    while p[0] == '\x00':
        print('removing x')
        p = p[1:]
    
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
    for i in range(1):
        t1 = time.time()
        print(phase())
        print(time.time() - t1)
        