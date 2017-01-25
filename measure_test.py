#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
measure currents using Keithley 6485 or 6487 picoammeter

Most recent changes: 1-11-2017 by Robert Stahulak
$Id: measure.py 13235 2012-10-02 17:43:24Z daumiller $
"""
from __future__ import division

import sys, os
import signal
import time
import datetime
import cPickle
import argparse
import random
import serial
import re

from Keithley_6485 import *
from UVLED import *
from LeCroy_9210 import *

def signal_handler(signal, frame):
    """ catch ctrl-C """
    print 'You pressed Ctrl-C!'
    sys.exit(0)

def screenOff(disable):
    """ switch off LCD backlight """
    print("screen off")
#    if disable:
#        os.system('xset dpms force off')
#    else:
#        os.system('xset dpms force on')

def execScript():
    """ reads and executes a scpi script """
    pico = Keithley6485()
    print pico.instrumentInfo()
    data = pico.execScript('example1.scpi')

    return data

def configure(pico, trigger='ARM', points=10, mRange=2E-2, nplc=1, debug=False):
    """ configure picoammeter to take data

    Parameters
    ----------
    pico: rs232 device instance
    mode:
        slow: each triggered separately
        fast: one trigger for all points
    N: number of points (<3000)
    debug: display each command and ackn

    Returns
    -------
    current, timestamps, errorCodes: 3 parallel lists
    """
    if trigger == 'ARM':
        pico.setDisplay('Slow:%.2f:%d' % (nplc, points))
    elif trigger == 'TRIG':
        pico.setDisplay('Fast:%.2f:%d' % (nplc, points))
    else:
        pico.setDisplay('Free:%.2f:%d' % (nplc, points))

    pico.setFunction('CURR')
    pico.setAutoRange(0)
    pico.setRange(mRange)
    pico.setIntegrationTime(nplc)
    # pico.setZeroCheck(0)
    pico.zeroCorrect()  # accuire a zero-correct value
    pico.setAutoZero(0) # 3 times faster
    pico.clear() # ?
    pico.setBufferSize(1)
    pico.clearBuffer()
    pico.setBufferSize(points)
    pico.clearBuffer()
    pico.setStorageControl()
    pico.enableBufferEvent()
    pico.enableSRQ()
    pico.setTriggerDelay(0)
    pico.setTriggerCount(points)

    pico.setDamping(0)          # by default on TODO Really OK?
    pico.write('TRIG:OLIN 2')   # generate trigger out signals on TLINK 2
    pico.write('TRIG:OUTP SENS')
    if trigger == 'TRIG':
        pico.write('ARM:SOUR IMM')
        pico.write('TRIG:SOUR TLIN')
    elif trigger == 'ARM':
        pico.write('ARM:SOUR TLIN')
        pico.write('TRIG:SOUR IMM')
    else:                       # no external triggers
        pico.write('ARM:SOUR IMM')
        pico.write('TRIG:SOUR IMM')

    pico.enableDisplay(False)
    pico.waitOperationCompleted()

def measure(pico):
    """ """
    print "will now take data, busy for at least %.3f seconds" % (pico.points * pico.nplc * 0.02)
    pico.setStorageControl() # start storing readings (needed!)
    pico.waitOperationCompleted()
    pico.clearTrigger()
    print "starting measurement"
    pico.init()   # start measurement at next trigger signal
    pico.waitOperationCompleted()
    t0 = time.time()
    print "done!"
    data = pico.getData()
    print "readout: %.2f s" % (time.time() - t0)

    return splitCTEData(data)

def finish(pico):
    """ """
    pico.setZeroCheck(True) # protect input
    pico.enableDisplay(True)

def getNextFilename(basename, ext='dump', maxCount=1000, dateprefix=True):
    """ build next filename """
    prefix = ""
    if dateprefix:
        prefix = datetime.datetime.now().strftime('%Y-%m-%d_')
        basename = prefix + basename
        if not os.path.exists(prefix):
            os.makedirs(prefix)
            uid = int(os.environ.get('SUDO_UID'))
            gid = int(os.environ.get('SUDO_GID'))
            os.chown(prefix,uid,gid)
    for i in xrange(maxCount):
        filename = "%s-%02i.%s" % (basename, i, ext)
        if prefix is not "":
            filename = prefix+"/"+filename
        if not os.path.exists(filename):
            return filename
    return None

def stdDev(a):
    numPoints = len(a)
    mean = sum(a)/numPoints
    differences = [x - mean for x in a]
    diffsSquared = [d ** 2 for d in differences]
    sumOfSqDiffs = sum(diffsSquared)
    standardDeviation = (sumOfSqDiffs/numPoints)**.5
    return standardDeviation
    
def storeData(filename, t, c, e, uvID, ampl, amprb, width, now, log=None, temperatures=None, cmdl_args=None):
    print "Writing data to %s .." % filename
    dataFile = open(filename, 'w')
    currentAverage = sum(c)/len(c)
    currentStD = stdDev(c)
    dataFile.write("UVLED ID,Average Current (A),Current StD (A),UVLED Amplitude (mA),UVLED Amplitude Readback (mA),UVLED Width (uS),Seperation (m),Pulse Frequency (Hz),External Temp,LED Temp,MC Temp\n")
    if len(temperatures) is not 0:
        dataFile.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n".format(uvID,currentAverage,currentStD,ampl,amprb,width,cmdl_args.distance,cmdl_args.frequency,temperatures[0][2],temperatures[1][2],temperatures[2][2]))
    else:
        dataFile.write("{0},{1},{2},{3},{4},{5},{6}\n".format(currentAverage,currentStD,ampl,amprb,width,cmdl_args.distance,cmdl_args.frequency))
    dataFile.write("Current (A),Time (s),Error State\n")
    for i in range(len(t)):
        dataFile.write("{0},{1},{2}\n".format( c[i], t[i], e[i]))
    #print "Writing data to %s .." % filename,
    #cPickle.dump({'timestamps': t,
    #            'currents': c,
    #            'errorCodes': e,
    #            'log': log,
    #            'temperatures': temperatures,
    #            'time': now,
    #            'args':cmdl_args},
    #            open(filename, 'w'), -1) 
    print "done!"


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(
                description='automatic readout of picoammeter ',
                epilog="(still under development (pre alpha ...) )")
    parser.add_argument(
                dest='outputBasename', metavar='basename',
                help='basename for created files')
    parser.add_argument(
                '-p', '--points', dest='npoints', type=int, default=100,
                metavar='N', help='number of points (triggers) the picoammeter takes, default: 100')
    parser.add_argument(
                '-m', '--measurements', type=int, default=1,
                metavar='N', help='number of measurents, default: 1')
    parser.add_argument(
                '-s', '--sleep', type=int, default=0,
                metavar='S', help='pause after a measurement in seconds, default: 0')
    parser.add_argument(
                '-N', '--Noreset', dest='reset', action='store_false',
                default=True, help='do not reset device at start and end')
    parser.add_argument(
                '-r', '--range', default=2E-2, type=float, metavar="range",
                choices=(2E-2, 2E-3, 2E-4, 2E-5, 2E-6, 2E-7, 2E-8, 2E-9),
                help='measurement range: 2E-2, 2E-3, ..., 2E-9, default: 2E-2')
    parser.add_argument(
                '-n', '--nplc', default=5., type=float,
                help='integration time in number of power line cycles, default: 5 (=100ms)')
    parser.add_argument(
                '-t', '--triggermode', choices=['ARM', 'TRIG'],
                help='select external trigger mode, default: None')
    parser.add_argument(
                '-a', '--amplitude', default=None,
                help='flasher: flash amplitude')
    parser.add_argument(
                '-w', '--width', default=None,
                help='flasher: flash width')
    parser.add_argument(
                '-c', '--comment', default=None,
                help='comment')
    parser.add_argument(
                '-q', '--quiet', action='store_true',
                help='no speech output')
    parser.add_argument(
                '-d', '--debug', action='store_true',
                help='enable debug mode')
    parser.add_argument(
                '-f', '--frequency', default=None,
                help='flash frequency set on the pulse generator to be stored alongside rest of data')
    parser.add_argument(
                '-di', '--distance', default=None,
                help='Distance from the flasher to the photodiode in meters')
    args = parser.parse_args()

    pico = Keithley6485('/dev/ttyUSB1', debug=args.debug)
    if args.reset:
        pico.reset()        # clickety-clack ...

    temperatures = list()
    if args.amplitude is not None: # attach only if needed
        print 'attaching flasher ...'
        uvled = UVLED('/dev/ttyUSB0',debug=args.debug)
        print "getting temperatures ..."
        temps = uvled.getTemps()
        ExtTemperature = float(temps[1])
        tnow = time.time()
        temperatures.append((1, tnow, ExtTemperature))
        LEDTemperature = float(temps[2])
        tnow = time.time()
        temperatures.append((2, tnow, LEDTemperature))
        MCTemperature = float(temps[3])
        tnow = time.time()
        temperatures.append((3, tnow, MCTemperature))
        print u'Temperatures: Ext: %.1f°, LED: %.1f°, MC: %.1f°' % (ExtTemperature, LEDTemperature, MCTemperature)
    else:
        uvled = None
        
    configure(pico, trigger=args.triggermode, points=args.npoints, debug=False, nplc=args.nplc, mRange=args.range)
    configLog = pico.log
    
    if args.amplitude is not None:
        uvled.setAmpl(float(args.amplitude))

    if args.width is not None:
        uvled.setWidth(float(args.width))

    if uvled is not None:
        uvledAmplitude = uvled.getAmpl()
        uvledAmpRB = uvled.getAmpRB()
        uvledWidth = uvled.getWidth()
        uvledID = uvled.getID()
        print "pulse amplitude: ", uvledAmplitude
        print "pulse amplitude readback: ", uvledAmpRB
        print "pulse width:", uvledWidth
    else:
        uvledAmplitude = None
        uvledWidth = None
        uvledAmpRB = None
        uvledID = None

    if args.frequency is not None:
        print 'attaching pulse generator'
        pulser = LeCroy_9210('/dev/ttyUSB1',debug=args.debug)
        pulser.setDisplay(False)
        pulser.setFreq(args.frequency)
        print "frequency is %d" % float(pulser.getFreq())
    else:
        pulser = None
        
    print "getting ready"
    screenOff(True)
    for cycle in range(args.measurements):  # do a set of measurements
        # Check the output filename
        filename = getNextFilename(args.outputBasename,"csv")
        if filename is None:
            print "No more files with this basename available."
            sys.exit()
        if uvled is not None:
            uvled.run()
        now = time.time()
        pico.log = list()
        c, t, e = measure(pico)
        print "received %d datapoints" % len(c)
        bad = sum(x != 0 for x in e)
        if bad:
            print('WARNING, %d errors' % bad)

        #if False and not bad:  # overflow measurements are skipped very fast -> not all flashes cleared in flasher
                     # TODO: check why Arduino software triggers don't work anymore

        storeData(filename, t, c, e, uvledID, uvledAmplitude, uvledAmpRB, uvledWidth, now, configLog + pico.log, temperatures, args)
        print 'cycle: %.2f s' % (time.time() - now)
        if cycle < args.measurements - 1:
            time.sleep(args.sleep)

    finish(pico)
    pico.setDisplay('Finished')
    
    if pulser is not None:
        pulser.setDisplay(True)
    #if uvled is not None:
        #uvled.run(False)
    screenOff(False)

        
    # TODO switch to hdf5?
