# main file to discipline the oscillator
# measures phase difference over time and uses an FFT to estimate frequency offset from reference

import cowbell_simulator as csim
import cowbell_io as cowbell
import sim_time as time
import numpy as np
import math
import sys

# whether the ULN is simulated
SIM = True
# sample rate in samples per second
SR = 10
# tuning slope magnitude in V/Hz, based on calculation from datasheet
M_TUNE = 2.5
# tuning voltage in V
v_tune = 0
# previous frequency offset for calculating tuning slope
prev_freq = -1
# sign of tuning voltage (positive will decrease frequency)
sign = 1
# string last printed using sys.stdout
pstr = ''

# function to clear line and print string s
def clear_print(s):
    global pstr

    # clear previous line
    sys.stdout.write('\r' + ' ' * len(pstr))
    sys.stdout.flush()
    # update pstr and print new line
    pstr = '\r' + s
    sys.stdout.write(pstr)
    sys.stdout.flush()

# function to find fundamental freq of signal
def fund(signal):
    # number of samples
    n = signal.size

    # take fourier transform
    transform = np.fft.fft(signal)
    # get magnitudes of complex numbers
    transform = abs(transform)
    # get array of frequency bin centers
    freqs = np.fft.fftfreq(n, d = 1/SR)
    # get rid of negative frequencies
    transform = transform[0 : math.ceil(n / 2)]
    freqs = freqs[0 : math.ceil(n / 2)]
    # return frequency with largest amplitude
    return freqs[transform.argmax()]

# function to convert seconds to minutes and seconds
def nice_time(s):
    sec = s % 60
    min = math.floor(s / 60)
    output = ('' if min == 0 else str(min) + ' minute' + ('s' if min > 1 else '')) + (', ' if min != 0 and sec != 0 else '') + ('' if sec == 0 else str(sec) + ' second' + ('s' if sec > 1 else '')) + ('0 seconds' if sec == 0 and min == 0 else '')
    
    return output

# function to collect 2^exp samples
def samp(exp):
    # create signal array of length 2**exp
    signal = np.zeros(2**exp)
    # time of previously collected sample
    prev_time = time.time()
    # total samples collected
    samples = 0
    # sample time
    samp_time = 1/SR

    # total time of FFT
    fft_time = round(2**exp * samp_time)
    # initialize time remaining to total time
    time_remaining = fft_time

    # collect samples
    while(samples < 2**exp):
        # increment time
        time.increment()
        # current time
        now = time.time()

        # don't do anything until sample time has passed
        if now - prev_time < samp_time:
            continue
        
        # measure phase and add it to signal array
        signal[samples] = cowbell.phase()
        # increment samples
        samples += 1
        # update prev_time
        prev_time = now

        # calculate and print time remaining
        time_remaining = round((1 - (samples / 2**exp)) * fft_time)
        clear_print(nice_time(time_remaining) + ' until next v_tune update')

    return signal

# function to tune clock using 2^exp samples
def tune(exp):
    global v_tune
    global prev_freq
    global sign

    # total time of fft
    t = 2**exp / SR
    # frequency precision of fft
    prec = 1 / t
    print('2^' + str(exp), 'samples:', prec, 'Hz precision in', round(t * 100 / 60) / 100, 'minutes')

    # get frequency offset
    freq = fund(samp(exp))

    # clear_print('freq: ' + str(csim.freq()) + '\n')

    clear_print('measured frequency offset: ' + str(freq) + ' Hz\n')

    # if it's not the first time
    if prev_freq != -1:
        # if offset is getting worse, change directions
        if prev_freq != 0 and freq > prev_freq:
            sign *= -1

    # print('sign:', sign)

    # update tuning voltage
    # multiply by 0.5 to overshoot less often
    v_tune += 0.5 * sign * M_TUNE * freq

    if v_tune > 5:
        v_tune = 5
    elif v_tune < -5:
        v_tune = -5

    if v_tune < 0:
        v_tune = 0

    cowbell.tune(v_tune)

    clear_print('tuning voltage: ' + str(v_tune) + ' V\n\n')

    # update previous frequency offset
    prev_freq = freq

if __name__ == "__main__":
    # tune clock with increasing precisions
    # more precision = longer measurement time
    # starting low precision allows it to act sooner

    for exp in range(6, 14):
        tune(exp)
    while(True):
        # time = 27min, precision = 0.0006Hz
        tune(14)
