# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 19:32:39 2016

@author: styku
"""

class InputHandler(object):
    
    class Mode():
        STANDBY = 0
        NORMAL = 1
        CALIBRATION = 2
        
    class Axis():
        LS_X = 0
        LS_Y = 1
        LT = 4
        RT = 5
        
    class EventTypes():
        ANALOG = 7
        BUTTON = 11  
        
    class Button():
        SELECT = 6
        Y = 3
        
    def __init__(self):
        self.threshold1 = 0.3
        self.threshold2 = 0.9
        
        #Action mapping
        self.command = {
            self.Mode.NORMAL: {
                self.EventTypes.ANALOG: {
                    self.Axis.LS_X: self.moveStrafe,
                    self.Axis.LS_Y: self.moveForward,
                    self.Axis.LT: self.moveLower,
                    self.Axis.RT: self.moveRise
                },
                self.EventTypes.BUTTON: {
                
                }
            },
            self.Mode.CALIBRATION: {
                self.EventTypes.ANALOG: {
                
                },
                self.EventTypes.BUTTON: {
                
                }
            },    
        }
        
    
    