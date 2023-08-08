# simulation of the cowbell (wenzel ultralow noise crystal oscillator) for testing purposes during development
# linear frequency drift
# these tune() and phase() functions can be used instead of the ones in cowbell_io.py

import sim_time as time
import random

# set initial time
t0 = time.time()
# set reference frequency to 10 MHz
fr = 10e6
# # set initial frequency to reference frequency plus or minus random offset
# f0 = fr * (1 + (random.randint(0, 1) * 2 - 1) * random.random() / 10**7)
# set initial frequency to reference frequency plus random offset
f0 = fr * (1 + random.random() / 10**7)
# aging rate in s^-1, 5e-10/day is from Wenzel ULN datasheet
r = 5e-10 / (24 * 60 * 60)

# tuning voltage -5 to 5
vtune = 0
# tuning slope, Hz/V (-4e-8 is from datasheet)
mtune = -4e-8 * fr
# total phase accumulated from tuning voltage, starts at random phase
ptune = random.random() * 360
# previous time ptune was updated, initialize to t0
t_updated = t0

def update_ptune():
    global ptune
    global t_updated
    now = time.time()
    # add the accumulated phase since last time it was updated
    ptune += mtune * vtune * (now - t_updated) * 360
    t_updated = now

# return frequency at time "now"
def freq():
    update_ptune()
    now = time.time()
    t = now - t0

    # linear model
    f = f0 + fr * r * t + vtune * mtune

    return f

# ADC for phase voltage
def adc(value, bits = 16, range = 1440):
    step = range / 2**bits
    return round(value / step) * step

# return phase difference in deg or mV depending on phase_detector boolean
def phase(phase_detector = True):
    update_ptune()
    now = time.time()
    t = now - t0

    # linear model of frequency drift --> quadratic phase difference
    p = (0.5 * fr * r * t**2 + (f0 - fr) * t) * 360 + ptune
    # degrees wrap around and round to 1 decimal place
    p = round((p + 180) % 360 - 180, 1)

    # convert from deg to mV if using phase detector
    # 8 mV/deg from datasheet, and 90 deg --> 0 mV
    if phase_detector:
        p = abs(p) * 8 - 90 * 8
        p = adc(p)

    return p

# function to convert to DAC output
def dac(value, bits = 16, range = 10):
    step = range / 2**bits
    return round(value / step) * step

# change the tuning voltage
def tune(v):
    global vtune
    update_ptune()
    vtune = dac(v)

if __name__ == "__main__":
    tune(3)
    while(True):
        print('phase:', phase(True))
        # increment time
        time.increment()
        # print('freq:', freq())
        # time.sleep(.2)