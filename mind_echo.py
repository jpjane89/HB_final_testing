#!/usr/bin/env python
# -*- coding:utf-8 -*-

import platform
import sys, time
from pymindwave import headset
from pymindwave.pyeeg import bin_power
import datetime


def connect():
    time.sleep(0.5)
    if hs.get_state() != 'connected':
        hs.disconnect()

    while hs.get_state() != 'connected':
        time.sleep(0.5)
        print 'current state: {0}'.format(hs.get_state())
        if (hs.get_state() == 'standby'):
            print 'trying to connect...'
            hs.connect()

    print 'now connected!'
    time.sleep(0.5)

def generate_stream():

    while True:
        if hs.parser.raw_values:
            v = hs.parser.raw_values.pop(0)
            yield v
        else:
            time.sleep(0.1)

def process_first_value():
    v = generate_stream().next()

    return v

def process_next_value(before_v):

    v = generate_stream().next()
    new_v = smooth_value(before_v, v)

    return new_v

def smooth_value(before_v, v):

    new_v = (before_v*0.6) + (0.4*v)
    return new_v

def interpret_value(before_v, v):

    delta = v - before_v
    print v, delta

    if v > 60000:
       print "You blinked"

    elif (v > 1000 or v < -1000):
        print "Physical movement"
        
    elif (delta > 15 or delta < -15):
        print "Large change"

    else:
        print "Normal"

def main():
    connect()

    generate_stream()

    smooth_values = []

    v = process_first_value()
    smooth_values.append(v)

    while True:
        next_v = process_next_value(smooth_values[-1])
        smooth_values.append(next_v)
        interpret_value(smooth_values[-2], smooth_values[-1])

if __name__ == "__main__":
    if platform.system() == 'Darwin':
        hs = headset.Headset('/dev/tty.MindWave')
    else:
        hs = headset.Headset('/dev/ttyUSB0')

    main()

    print 'disconnecting...'
    hs.disconnect()
    hs.destroy()
    sys.exit(0)

