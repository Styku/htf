import pygame
import XboxController
import time
from subprocess import call
from Hexapod import Hexapod
from ServoDriver import ServoDriver

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
        print self.robot.legs[0].coxa.getCommand()
        
    def saveCalibrationData(self):
        f = open("calib.dat", "w+")   
        for i in range(6):
            f.write("%d\n" % self.robot.legs[i].coxa.calibration)
            f.write("%d\n" % self.robot.legs[i].femur.calibration)
            f.write("%d\n" % self.robot.legs[i].tibia.calibration)
        f.close()
        
    def speak(self, text):
        call(["espeak", "-ven+m5", "-k6", "-s150", text])
    
    def loadCalibrationData(self):
        f = open("calib.dat", "r")
        lines = f.read().splitlines()
        print "Loading calibration data: "
        for i in range(6):
            print("Leg %d: [%s] [%s] [%s]" % (i,lines[i*3],lines[i*3+1],lines[i*3+2]))
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
                    elif event.axis == 0: #STRAFE
                        if event.value < -0.3:
                            self.action[self.Action.STRAFE_RIGHT]=True
                            self.speed = 2 if abs(event.value)>0.9 else 1
                        elif event.value >= -0.3 and event.value <= 0.3:
                            self.action[self.Action.STRAFE_RIGHT]=False
                            self.speed = 0
                        else:
                            self.action[self.Action.STRAFE_RIGHT]=True
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
                    #self.speak("Calibration mode on")
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
