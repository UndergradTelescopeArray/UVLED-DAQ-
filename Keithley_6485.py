# -*- coding: utf-8 -*-

# very quick and dirty stuff for the Keithley 6485 / 6487 picoammeters

# $Id: Keithley_6485.py 13208 2012-09-17 14:43:49Z daumiller $

import sys, os
import serial
import time
import re

def splitFilename(fname):
    basename = os.path.basename(fname)
    name, ext = os.path.splitext(basename)
    m = re.match('(.*)-(\d{2})', name)
    base, idx = m.groups()
    
    return base, idx


def splitCTEData(data):
    """ split current/timestamp/error data into 3 1-d arrays """
    try:
        data = data.split(',')  # just a long list: c,t,e,c,t,e, ...
        currents = [float(d[:-1]) for d in data[::3]] # skip the 'A'
        timestamps = map(float, data[1::3])
        errorCodes = map(float, data[2::3])
    except Exception as err:
        print "Error while interpreting received data:"
        print err
        return None

    return currents, timestamps, errorCodes

class Keithley6485:
    """ provides some methods to access a Keithley picoammeter """
    def __init__(self, portName = '', name="Keithley6485", debug=False):
        """ connect to serial device """
        self.debug = debug
        self.verbose = 0
        try:
            self.dev = serial.Serial(portName,9600, timeout=.5)
            print('Connected to picoammeter')
        except serial.SerialException:
            sys.exit('Doh! What picoammeter?')

        self.log = list()
        self.mRange = None
        self.nplc = None
        self.points = None
        self.write('++mode 1')
        
    def read(self):
        self.dev.write('++addr 14\n')
        self.dev.write('++auto 1\n')
        """ wait for data, then read it"""
        time.sleep(1)     # TODO maybe loop is not needed, check dev.read()
        s = False
        while not s:
            s = self.dev.readline()
            time.sleep(1)     # TODO maybe loop is not needed, check dev.read()
        return s

    def write(self, string):
        """ generic write, to send arb. commands to the device """
        self.dev.write('++addr 14\n')
        self.dev.write('++auto 0\n')
        self.log.append(string)
        self.dev.write(string+"\n")

    def setDisplay ( self, text="TESTING...", option=1 ):
        """ Display a message on the front panel """
        # Remove current text
        if option == 0:
            self.write ( "D0X" )
        else:
            self.write ( ":DISP:WIND:TEXT:STAT 1;" )
            self.write ( ":DISP:WIND%d:TEXT:DATA \"%s\""%(option,text) )

    def setFunction(self, func='CURR'):
        self.write( 'FUNC "%s"' % func)

    def setTriggerDelay(self, delay):
        self.write( "TRIG:DEL %d" % delay)

    def setTriggerCount(self, count):
        self.write('TRIG:COUNT %d' % count)
        self.points = count

    def getTriggerCount(self):
        self.write('TRIG:COUNT?')
        count = self.read()
        return int(count)
        
    def clearTrigger(self):
        """ """
        self.write("TRIG:CLE")

    def setAutoRange(self, mode=0):
        if mode:
            self.write("SENS:CURR:RANG:AUTO ON")
        else:
            self.write("SENS:CURR:RANG:AUTO OFF")

    def setIntegrationTime(self, nplc=1):
        """ integration time in 'number of power line cycles'
        at 50 Hz: NPLC=1 <-> 20ms integration time
        
        Parameter
        ---------
        nplc  valid range: 0.01 - 50, float
        """
        
        self.write("SENS:CURR:NPLC %.3f" % nplc)
        self.nplc = nplc

    def setRange(self, mRange):
        """ Current measurement range, in Ampere

        Parameter
        ---------
        mRange  valid range: 2.E-2, 2.E-3, ... , 2.E-9, float
        """
        self.write("SENS:CURR:RANG %e" % mRange)
        self.mRange = mRange

    def setZeroCheck(self, check=0):
        """ """
        if check:
            self.write("SYST:ZCH ON")
        else:
            self.write("SYST:ZCH OFF")

    def setDamping(self, check=0):
        """ """
        if check:
            self.write("DAMP ON")
        else:
            self.write("DAMP OFF")

    def setAutoZero(self, auto=0):
        """ """
        if auto:
            self.write("SYST:AZER:STAT ON")
        else:
            self.write("SYST:AZER:STAT OFF")

    def enableDisplay(self, enable=0):
        """ """
        if enable:
            self.write("DISP:ENAB ON")
        elif not self.debug:
            self.write("DISP:ENAB OFF")

    def setBufferSize(self, size=0): # max 2500
        """ """
        self.write("TRAC:POIN %d" % size)

    def clearBuffer(self):
        """ """
        self.write("TRAC:CLE")

    def setStorageControl(self, control='NEXT'):
        """ """
        self.write("TRAC:FEED:CONT %s " % control)

    def enableBufferEvent(self, val=512):
        """ """
        self.write("STAT:MEAS:ENAB %s " % val)

    def enableSRQ(self, val=1):
        """ """
        self.write("*SRE %d " % val)

    def operationComplete(self):
        """ just send querystring """
        self.write("*OPC?")

    def waitOperationCompleted(self):
        """ queries and waits until operation is complete """
        self.operationComplete()
        self.read()

    def init(self):
        """ """
        self.write("INIT")

    def getData(self):
        self.write("TRAC:DATA?")
        return self.read()

    def clear ( self ):
        """ clear the instrument setup. Software reset. """
        self.write( "*CLS" )

    def reset ( self ):
        """ reset all (?) device settings """
        self.write("*RST")

    def instrumentInfo ( self ):
        """ Provides information on the attached device. """
        self.write( "*IDN?" )
        return self.read().strip()

    def zeroCorrect(self):
        """ performs a zero correction for the selected meas. range.
        see ref. man. 3-7
        """
        self.setZeroCheck(True)
        self.init()
        self.setZeroCheck(False)
        self.write("SYST:ZCOR:ACQ")
        self.setZeroCheck(False)
        self.write("SYST:ZCOR ON")


    def execScript(self, filename, verbose=False):
        """ execute a series of SCPI commands """
        for line in (l.strip() for l in open(filename, 'r')):
            line = line.replace("'", "#") # original examples use "'" as comment character, allow "cut and paste"
                                          # or maybe better switch to Keithley notation?
            if verbose and line.startswith('#'): # Allow comment lines
                print line
                continue
            if verbose:
                print ">>", line
            line = line.split('#')[0].strip() # strip end-of-line comments
            self.write(line)

            if line == '*OPC?':  # Wait for answer
                answer = self.read()
                if verbose:
                    print "<<", answer,

                if answer.strip() != '1':
                    print "Received unexpected answer: >%s<" % answer
                    sys.exit(1)
            elif line == 'TRAC:DATA?':      # Receive measurements
                data = self.getData()
                print "finished measurement"
            elif line == 'READ?':           # measure and read directly
                data = self.getData()
            elif line == 'INIT':
                print "start measurement"

            time.sleep(0.01) # not sure if this is really needed ...

        return data
