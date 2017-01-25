# -*- coding: utf-8 -*-

import sys, os
import serial
import time
import re

class LeCroy_9210:
    def __init__(self, portName = '', name="UVLED", debug=False):
        """ connect to serial device """
        self.debug = debug
        self.verbose = 0
        try:
            self.dev = serial.Serial(portName,9600, timeout=.5)
            print('Also connected to pulse generator')
        except serial.SerialException:
            sys.exit('Shoot. Where\'s da Pulse Generator?')

        self.log = list()
        self.mRange = None
        self.nplc = None
        self.points = None
        self.write('++mode 1')
        
    def read(self):
        self.dev.write('++addr 13\n')
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
        self.dev.write('++addr 13\n')
        self.dev.write('++auto 0\n')
        self.log.append(string)
        self.dev.write(string+"\n")

    def setFreq(self, freq):
        #The LeCroy command has the format "freq x" where x may(must?) be expressed with units, i.e. 30M for 30 Megahertz
        if float(freq) < 130000:
            self.write("freq %d" % float(freq))
        else:
            print "Requested frequency outside safety parameters"
            print "Exiting..."
            self.setDisplay(True)
            sys.exit()

    def getFreq(self):
        self.write("freq?")
        freq = self.read()
        return freq

    def setDisplay(self, state = False):
        if state:
            self.write("disp on")
            self.write("bri 12")
        else:
            self.write("disp off")
            self.write("bri 1")

    def setEnabled(self, state = True):
        if state:
            self.write("A:DISA OFF")
            self.write("B:DISA OFF")
        else:
            self.write("A:DISA ON")
            self.write("B:DISA ON")

    
