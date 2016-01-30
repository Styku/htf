# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 20:55:12 2016

@author: styku
"""
import Adafruit_SSD1306

import Image
import ImageDraw
import ImageFont

class Display(object):
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=24)
        self.disp.begin()
        self.disp.clear()
        self.font = ImageFont.load_default()
        self.calib_image = [None]*18
        self.hexapod_image = Image.open('img/hexapod.ppm').convert('1')
        for i in range(18):       
            self.calib_image[i] = Image.open("img/hexapod%d.ppm" % (i+1)).convert('1')
        
    def calibration(self,i):
        self.disp.image(self.calib_image[i])
        self.disp.display()
