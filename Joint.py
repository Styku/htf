import numpy as np
import pygame
import XboxController
import time
import serial
import math

class Joint(object):
    def __init__(self):
        self.absoluteCenter = 1500
        self.center = 1500
        self.pos = self.center
        self.mvRange = 300
        self.maxPos = self.center + self.mvRange
        self.minPos = self.center - self.mvRange 
        self.port = 0
        self.maxT = 80 
        self.side = -1
        self.phase = 0
        self.centerRange = 500
        self.calibration = 0
        
    def changeCenter(self, c):
        if self.center + c <= self.absoluteCenter + self.centerRange and self.center + c >= self.absoluteCenter - self.centerRange:
            self.center += c*self.side
            self.maxPos = self.center + self.mvRange
            self.minPos = self.center - self.mvRange 

    def getPosition(self):
        return self.pos + self.calibration
        
    def calibrate(self, n):
        if abs(self.calibration + n) < 200:
            self.calibration += n
        
    def moveCenter(self):
        self.pos = self.center
        return ("#%d P%d" % (self.port, self.center))

    def moveCoxa(self, t):
        if self.phase == 1:
            t += self.maxT/4
        if self.phase == 0 or t >= self.maxT/2:
            t = t%self.maxT
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(2*(np.pi/self.maxT)*t))

    def moveFemur(self, t):
        if self.phase == 1:
            t += self.maxT/4
        if self.phase == 0 or t >= self.maxT/2:
            t = t%self.maxT
            if (t <= self.maxT/4 or (t > self.maxT/2 and t <= (3*self.maxT)/4)):
                self.pos = self.center + self.side*abs(self.mvRange*np.sin(4*(np.pi/(self.maxT))*t))

    def strafeTibia(self, t):
        if self.phase == 1:
            t += self.maxT/4
        if self.phase == 0 or t >= self.maxT/2:
            t = t%self.maxT
            self.pos = self.center + abs(self.mvRange*np.sin(2*(np.pi/self.maxT)*t))
    
    def getCommand(self):
        return ("#%d P%d" % (self.port, self.pos + self.calibration))