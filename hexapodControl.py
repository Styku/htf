import pygame
import XboxController
import os, sys
import threading
import time
import serial

limb = 0
move = 0
pos = 1500

port = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=115200
)

port.write("#0 P1500\r")

ctrl = XboxController.XboxController(None, deadzone = 30, scale = 100, invertYAxis = True)

def limbControl(val):
    global limb
    if val == 0:
        limb = (limb+1)%7
        print "{} limb selected".format(limb)

def limbForward(val):
    global move
    move = val

ctrl.setupControlCallback(ctrl.XboxControls.RB, limbControl)
ctrl.setupControlCallback(ctrl.XboxControls.LTHUMBY, limbForward)



counter = 0
try:
    ctrl.start()
    print "Controller support is running"
    while True:
        time.sleep(0.001)
        counter = counter + 1

        if counter == 50:
            counter = 0
            port.write("#0 P%d\r" % (pos + move))
            pos+=move
            print "Current possition: {}".format(pos)

except KeyboardInterrupt:
    print "User terminated"

except:
    print "Unexpected error: ", sys.exc_info()[0]
    raise

finally:
    ctrl.stop()
