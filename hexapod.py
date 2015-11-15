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
    def changeCenter(self, c):
        if self.center + c <= self.absoluteCenter + self.centerRange and self.center + c >= self.absoluteCenter - self.centerRange:
            self.center += c*self.side
            self.maxPos = self.center + self.mvRange
            self.minPos = self.center - self.mvRange 
        
    def moveCenter(self):
        self.pos = self.center
        return ("#%d P%d" % (self.port, self.center))

    def moveCoxa(self, t):
        if self.phase == 1:
            t += self.maxT/4
        if self.phase == 0 or t >= self.maxT/2:
            t = t%self.maxT
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(2*(np.pi/self.maxT)*t))

        return ("#%d P%d" % (self.port, self.pos))

    def moveFemur(self, t):
        if self.phase == 1:
            t += self.maxT/4
        if self.phase == 0 or t >= self.maxT/2:
            t = t%self.maxT
            if (t <= self.maxT/4 or (t > self.maxT/2 and t <= (3*self.maxT)/4)):
                self.pos = self.center + self.side*abs(self.mvRange*np.sin(4*(np.pi/(self.maxT))*t))
        return ("#%d P%d" % (self.port, self.pos))

    def strafeTibia(self, t):
        if self.phase == 1:
            t += self.maxT/4
        if self.phase == 0 or t >= self.maxT/2:
            t = t%self.maxT
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(2*(np.pi/self.maxT)*t))

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
    
    def connectDriver(self, drv):
        self.driver = drv

    def checkLegs(self):
        for i in range(6):
            print("Leg %d, side %d, port %d \n" % (i, self.legs[i].side, self.legs[i].port));

    def moveForward(self, state):
        for i in range(6):
            self.driver.sendCommand(self.legs[i].coxa.moveCoxa(state))
            self.driver.sendCommand(self.legs[i].femur.moveFemur(state))

    def strafeRight(self, state):
        for i in range(6):
            self.driver.sendCommand(self.legs[i].tibia.strafeTibia(state))
            self.driver.sendCommand(self.legs[i].femur.moveFemur(state))

    def stand(self):
        for i in range(6):
            self.driver.sendCommand(self.legs[i].coxa.moveCenter())
            self.driver.sendCommand(self.legs[i].femur.moveCenter())
            self.driver.sendCommand(self.legs[i].tibia.moveCenter())
    
    def up(self):
        for i in range(6):
            self.legs[i].tibia.changeCenter(-5)
            self.legs[i].femur.changeCenter(-5)
            self.driver.sendCommand(self.legs[i].tibia.moveCenter())
            self.driver.sendCommand(self.legs[i].femur.moveCenter())

    def down(self):
        for i in range(6):
            self.legs[i].tibia.changeCenter(5)
            self.legs[i].femur.changeCenter(5)
            self.driver.sendCommand(self.legs[i].tibia.moveCenter())
            self.driver.sendCommand(self.legs[i].femur.moveCenter())

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
    
    class Action():
        STAND = 0
        FORWARD = 1
        BACKWARD = 2
        STRAFE_LEFT = 3
        STRAFE_RIGHT = 4
        TURN_LEFT = 5
        TURN_RIGHT = 6
        UP = 7
        DOWN = 8

    def __init__(self):
        self.state = 0
        self.idle = 0
        self.speed = 0
        self.idle_threshold = 200
        self.robot = Hexapod()
        self.driver = ServoDriver()
        self.robot.connectDriver(self.driver)
        self.action = [True,False,False,False,False,False,False,False,False]
        self.pad = XboxController.XboxController(None, deadzone = 30, scale = 100, invertYAxis = True)
    
    def getInput(self):
        moved = False;
        for event in pygame.event.get():
            print event.axis
            print event.value
            if event.type == 7: #left analog
                if event.axis == 1:
                    if event.value < -0.3:
                        self.action[self.Action.FORWARD]=True
                        self.speed = 2 if abs(event.value)>0.9 else 1
                    elif event.value >= -0.3 and event.value <= 0.3:
                        self.action[self.Action.FORWARD]=False
                        self.speed = 0
                    else:
                        self.action[self.Action.FORWARD]=True
                        self.speed = -2 if abs(event.value)>0.9 else -1
                elif event.axis ==5: #Right Trigger 
                    if event.value > 0:
                        self.action[self.Action.UP]=True
                    else:
                        self.action[self.Action.UP]=False

                elif event.axis ==2: #Left Trigger 
                    if event.value > 0:
                        self.action[self.Action.DOWN]=True
                    else:
                        self.action[self.Action.DOWN]=False

        if sum(self.action) == 0:
            self.action[self.Action.STAND] = True

    def run(self):
        print("Controller support is running")
        while True: 
            self.getInput()

            if self.action[self.Action.FORWARD]:
                self.state += self.speed
                self.robot.moveForward(self.state)
            elif self.action[self.Action.STRAFE_RIGHT]:
                self.state += self.speed
                self.robot.strafeRight(self.state)
            elif self.action[self.Action.UP]:
                self.robot.up()
            elif self.action[self.Action.DOWN]:
                self.robot.down()
            elif self.action[self.Action.STAND]:
                self.state = 0
                self.robot.stand()
            
            self.driver.executeCommand()
            #pygame.event.clear()
            time.sleep(0.020)

controller = Controller()
controller.run()
