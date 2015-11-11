import numpy as np
import pygame
import XboxController
import os, sys
import threading
import time
import serial
import math

class Joint(object):
    def __init__(self):
        self.center = 1500
        self.pos = self.center
        self.maxPos = 1800
        self.minPos = 1200
        self.mvRange = self.maxPos-self.center
        self.port = 0
        self.maxT = 40 
        self.side = -1
        self.phase = 0

    def moveCoxa(self, t):
        if self.phase == 1:
            t += self.maxT/4

        t = t%self.maxT
        if t <= self.maxT/2 and self.phase == 0:
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(2*(np.pi/self.maxT)*t))
        if t > self.maxT/2 and self.phase == 1:
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(2*(np.pi/self.maxT)*t))
        return ("#%d P%d" % (self.port, self.pos))

    def moveFemur(self, t):
        if self.phase == 1:
            t += self.maxT/4

        t = t%self.maxT
        if t <= self.maxT/4 and self.phase == 0:
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(4*(np.pi/(self.maxT))*t))
        if t > self.maxT/2 and t <= (self.maxT*3)/4 and self.phase == 1:
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(4*(np.pi/(self.maxT))*t))
        return ("#%d P%d" % (self.port, self.pos))

class Leg(object):
    RIGHT = -1
    LEFT = 1

    def __init__(self):
        self.side = self.RIGHT
        self.coxa = Joint()
        self.femur = Joint()
        self.tibia = Joint()

    def setPort(self, port):
        self.coxa.port = port
        self.femur.port = port+1
        self.tibia.port = port+2

    def setSide(self, side):
        self.coxa.side = side
        self.femur.side = side
        self.tibia.side = side

    def setPhase(self, phase):
        self.coxa.phase = phase
        self.femur.phase = phase
        self.tibia.phase = phase

class Hexapod(object):
    """ Hexapod representation, holding an internal model 
        of the robot and taking care of inverse kinematics,
        trajectory planning/interpolation and so on.
    """

    def __init__(self):
        self.legs = [Leg() for i in range(6)]

        for i in range(3):
            self.legs[i].setSide(Leg.RIGHT)
            self.legs[i+3].setSide(Leg.LEFT)

        for i in range(6):
            self.legs[i].setPort(i*4)

        for i in [0,2,4]:
            self.legs[i].setPhase(0)

        for i in [1,3,5]:
            self.legs[i].setPhase(1)

    def checkLegs(self):
        for i in range(6):
            print("Leg %d, side %d, port %d \n" % (i, self.legs[i].side, self.legs[i].port));

class ServoDriver(object):
    def __init__(self, devport="/dev/ttyACM0", devbaudrate=115200):
        self.port = serial.Serial(
            port=devport,
            baudrate=devbaudrate
        )

    def sendCommand(self, cmd):
        self.port.write(cmd + " ")

    def executeCommand(self):
        self.port.write("\r")


class Controller(object):
    
    def __init__(self):
        self.state = 0
        self.robot = Hexapod()
        self.driver = ServoDriver()
        self.forward = False
        self.pad = XboxController.XboxController(None, deadzone = 30, scale = 100, invertYAxis = True)

        #pad.setupControlCallback(ctrl.XboxControls.LTHUMBY, self.forward)

    def forward(self, val):
        if False == self.moved:
            self.state += 1
            self.state = self.state%30
            self.moved = True

    def run(self):
        print("Controller support is running")
        while True: 
            event = pygame.event.poll();
            if event.type == 7 and event.axis == 1: 
                print(event.value)
                if event.value < -0.3:
                    self.forward = True
                elif event.value >= -0.3:
                    self.forward = False

            if self.forward == True:
                self.state += 1
            #print event.type

            for i in [0,1,2,3,4,5]:
                self.driver.sendCommand(self.robot.legs[i].coxa.moveCoxa(self.state))
                self.driver.sendCommand(self.robot.legs[i].femur.moveFemur(self.state))
           
            self.driver.executeCommand()
            #pygame.event.clear()
            time.sleep(0.020)

controller = Controller()
controller.run()
