import pygame
import XboxController
import os, sys
import threading
import time
import serial
import numpy as np
import math
import hexapod

limb = 0
move = [0]*24
pos = [1500]*24
moved = [False]*24

min_angle = 1000
max_angle = 2000

port = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=115200
)

for i in range(24):
    port.write("#%d P1500" % i)
    time.sleep(0.005)
    port.write("\r")
    time.sleep(0.005)

ctrl = XboxController.XboxController(None, deadzone = 30, scale = 100, invertYAxis = True)

def limbControl(val):
    global limb
    if val == 0:
        limb = (limb+1)%7
        print "{} limb selected".format(limb)

def limbForward(val):
    global move
    global moved
    for i in [0,8,16]:
        move[i] = math.floor(-val/2)
        moved[i] = True

def posUp(val):
    global move
    global moved
    for i in [1,5,9]:
        move[i] = math.floor(val/2)
        moved[i] = True
    for i in [13,17,21]:
        move[i] = math.floor((-val)/2)
        moved[i] = True

def posDown(val):
    global move
    global moved
    for i in [1,5,9]:
        move[i] = math.floor((-val)/2)
        moved[i] = True
    for i in [13,17,21]:
        move[i] = math.floor(val/2)
        moved[i] = True

def resetPosition(val):
    for i in range(24):
        port.write("#%d P1500\r" % i)

    for i in range(24):
        global pos
        pos[i] = 1500
    
ctrl.setupControlCallback(ctrl.XboxControls.RB, limbControl)
ctrl.setupControlCallback(ctrl.XboxControls.LTHUMBY, limbForward)
ctrl.setupControlCallback(ctrl.XboxControls.RTRIGGER, posUp)
ctrl.setupControlCallback(ctrl.XboxControls.LTRIGGER, posDown)
ctrl.setupControlCallback(ctrl.XboxControls.XBOX, resetPosition)


try:
    ctrl.start()
    print "Controller support is running"
    while True:

        for i in range(24):
            pos[i]+=move[i]

            if pos[i] > max_angle:
                pos[i] = max_angle
            elif pos[i] < min_angle:
                pos[i] = min_angle
           
            if moved[i]:
                port.write("#%d P%di " % (i, pos[0]))
                #time.sleep(0.005)
                #port.write("\r")
                #time.sleep(0.005)
                moved[i] = False

        time.sleep(0.020)
        port.write("\r")
        print "Current possition: {}".format(pos)

except KeyboardInterrupt:
    print "User terminated"

except:
    print "Unexpected error: ", sys.exc_info()[0]
    raise

finally:
    ctrl.stop()
