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
            self.pos = self.center + self.side*abs(self.mvRange*np.sin(2*(np.pi/self.maxT)*t))
    
    def getCommand(self):
        return ("#%d P%d" % (self.port, self.pos + self.calibration))

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
            self.legs[i].coxa.moveCoxa(state)
            self.legs[i].femur.moveFemur(state)
            self.driver.sendCommand(self.legs[i].coxa.getCommand())
            self.driver.sendCommand(self.legs[i].femur.getCommand())

    def strafeRight(self, state):
        for i in range(6):
            self.legs[i].tibia.strafeTibia(state)
            self.legs[i].femur.moveFemur(state)
            self.driver.sendCommand(self.legs[i].tibia.getCommand())
            self.driver.sendCommand(self.legs[i].femur.getCommand())

    def stand(self):
        for i in range(6):
            self.legs[i].coxa.moveCenter()
            self.legs[i].femur.moveCenter()
            self.legs[i].tibia.moveCenter()
            self.driver.sendCommand(self.legs[i].coxa.getCommand())
            self.driver.sendCommand(self.legs[i].femur.getCommand())
            self.driver.sendCommand(self.legs[i].tibia.getCommand())
            
    def calibrate(self, leg, c=0, f=0, t=0):
        self.legs[leg].coxa.calibrate(c)
        self.legs[leg].femur.calibrate(f)
        self.legs[leg].tibia.calibrate(t)
        self.driver.sendCommand(self.legs[leg].coxa.getCommand())
        self.driver.sendCommand(self.legs[leg].femur.getCommand())
        self.driver.sendCommand(self.legs[leg].tibia.getCommand())
    
    def up(self):
        for i in range(6):
            self.legs[i].tibia.changeCenter(-5)
            self.legs[i].femur.changeCenter(-5)
            self.legs[i].tibia.moveCenter()
            self.legs[i].femur.moveCenter()
            self.driver.sendCommand(self.legs[i].tibia.getCommand())
            self.driver.sendCommand(self.legs[i].femur.getCommand())

    def down(self):
        for i in range(6):
            self.legs[i].tibia.changeCenter(5)
            self.legs[i].femur.changeCenter(5)
            self.legs[i].tibia.moveCenter()
            self.legs[i].femur.moveCenter()
            self.driver.sendCommand(self.legs[i].tibia.getCommand())
            self.driver.sendCommand(self.legs[i].femur.getCommand())

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
        INCREASE = 9
        DECREASE = 10
        
    class Mode():
        STANDBY = 0
        NORMAL = 1
        CALIBRATION = 2

    def __init__(self):
        self.state = 0
        self.idle = 0
        self.speed = 0
        self.idle_threshold = 200
        self.robot = Hexapod()
        self.driver = ServoDriver()
        self.robot.connectDriver(self.driver)
        self.action = [True,False,False,False,False,False,False,False,False,False,False]
        self.pad = XboxController.XboxController(None, deadzone = 30, scale = 100, invertYAxis = True)
        self.mode = self.Mode.NORMAL
        self.calibration = 0;
        self.loadCalibrationData()
        
    def saveCalibrationData(self):
        f = open("calib.dat", "w+")   
        for i in range(6):
            f.write("%d\n" % self.robot.legs[i].coxa.calibration)
            f.write("%d\n" % self.robot.legs[i].femur.calibration)
            f.write("%d\n" % self.robot.legs[i].tibia.calibration)
        f.close()
    
    def loadCalibrationData(self):
        f = open("calib.dat", "r")
        lines = f.read().splitlines()
        for i in range(6):
            self.robot.legs[i].coxa.calibration = int(lines[i*3])
            self.robot.legs[i].femur.calibration = int(lines[i*3+1])
            self.robot.legs[i].tibia.calibration = int(lines[i*3+2])
        f.close()
        
    def getInput(self):
        for event in pygame.event.get():
            print event
            if event.type == 7:
                if self.mode == self.Mode.NORMAL: #left analog
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
                elif self.mode == self.Mode.CALIBRATION:
                    if event.value < -0.3:
                        self.action[self.Action.INCREASE]=True
                        self.speed = 2 if abs(event.value)>0.9 else 1
                    elif event.value >= -0.3 and event.value <= 0.3:
                        self.action[self.Action.FORWARD]=False
                        self.speed = 0
                    else:
                        self.action[self.Action.DECREASE]=True
                        self.speed = -2 if abs(event.value)>0.9 else -1
            elif event.type == 11 and event.button == 6:
                if self.mode != self.Mode.CALIBRATION: #select
                    print "Calibration mode on"
                    self.mode = self.Mode.CALIBRATION
                    print self.mode
                else:
                    print "Calibration mode off"
                    self.saveCalibrationData()

                    self.mode = self.Mode.NORMAL
            elif event.type == 11 and event.button == 3:
                if self.mode == self.Mode.CALIBRATION: #select
                    if self.calibration == 17:
                        self.calibration = 0
                    else:
                        self.calibration += 1
                    print "Limb %d selected" % self.calibration
        
                    
        if sum(self.action) == 0:
            self.action[self.Action.STAND] = True

    def run(self):
        print("Controller support is running")
        while True: 
            self.getInput()

            if self.mode == self.Mode.NORMAL:
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
            if self.mode == self.Mode.CALIBRATION:
                if self.action[self.Action.INCREASE]:
                    c = 0
                    f = 0
                    t = 0
                    leg = int(self.calibration / 3)
                    if self.calibration % 3 == 0:
                        c = self.speed
                    elif self.calibration % 3 == 1:
                        f = self.speed
                    else:
                        t = self.speed
                
                    self.robot.calibrate(leg, c, f, t)
                   
                
            self.driver.executeCommand()
            #pygame.event.clear()
            time.sleep(0.020)

controller = Controller()
controller.run()
