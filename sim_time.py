# allows use of simulated time or real time
# make sure to use real time when using a real oscillator

import time as realtime

# higher timescale = slower time (one tick of simulated time is one second / timescale)
timescale = 1000

# time in units of [seconds / timescale]
t = 0

# whether to use simulated time
SIM = False

# return either simulated time or real time (both in seconds)
def time():
    return t / timescale if SIM else realtime.time()

# increment time by one tick
def increment():
    global t
    t += 1