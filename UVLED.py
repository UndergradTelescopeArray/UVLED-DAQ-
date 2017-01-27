# -*- coding: utf-8 -*-

import sys, os
import serial
import time
import re

class UVLED:
    def __init__(self, portName = '', name="UVLED", debug=False):
        """ connect to serial device """
        self.debug = debug
        self.verbose = 0
        try:
            self.dev = serial.Serial(portName,9600, timeout=.5)
            print('Connected to UVLED')
        except serial.SerialException:
            sys.exit('Darn. What UVLED?')

        self.log = list()
        self.mRange = None
        self.nplc = None
        self.points = None

        self.write("echo off")
	self.write("count 0")
        self.setTrig("xt")
        #self.setTrig("DC")
        
    def read(self):
        """ wait for data, then read it"""
        time.sleep(1)     # TODO maybe loop is not needed, check dev.read()
        s = False
        while not s:
            s = self.dev.readline()
            time.sleep(1)     # TODO maybe loop is not needed, check dev.read()
        return s

    def write(self, string):
        """ generic write, to send arb. commands to the device """
        self.dev.reset_input_buffer()
        self.log.append(string)
        self.dev.write(string+"\n")
        time.sleep(.1)

    def setTemp(self, temp):
        self.write("tset %d" % temp)

    def getTemps(self):
        self.write("temp")
        temps = re.split("A |B |C |D ", self.read())
        return temps

    def setWidth(self, width):
        self.write("width %d" % width)

    def getWidth(self):
        self.write("width")
        width = float(self.read().split(" ")[1])
        return width

    def setAmpl(self, amplitude):
        self.write("ampl %d" % amplitude)
 
    def getAmpl(self):
        self.write("ampl")
        ampl = float(self.read().split(" ")[1])
        return ampl

    def getAmpRB(self):
        self.write("amprb")
        amprb = float(self.read().split(" ")[1])
        return amprb

    def setTrig(self, trig):
        self.write("trig %s" % trig)

    def getTrig(self):
        self.write("trig")
        trig = self.read().split(" ")[1]
        return trig

    def getPulseCount(self):
        self.write("count")
        counts = int(float(self.read().split(" ")[1]))
        return counts

    def getID(self):
        self.write("id")
        uvID = self.read()[:-2]
        return uvID

    def run(self, state = True):
        if state:
            self.write("run on")
        else:
            self.write("run off")
        

    
