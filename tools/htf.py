import os
import pygame
import time
import random
import XboxController 
import serial

class htf:
    screen = None;
    gui_image = None;
    limbs = ["No", "Rear left", "Rear right", "Middle left", "Middle right", "Front left", "Front right"] 
    run = True
    logging = 1

    def log(self, msg, lvl = 1):
        if self.logging >= lvl:
            print msg

    def initDisplay(self):
        os.environ["SDL_FBDEV"] = "/dev/fb1"
        os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        os.environ["SDL_VIDEODRIVER"] = "fbcon"

        pygame.display.init()
        pygame.mouse.set_visible(False)

        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.log("Framebuffer size: %d x %d" % (size[0], size[1]))
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def loadResources(self):
        self.images = []
        self.images.append(pygame.image.load("img/gui.png"))
        self.images.append(pygame.image.load("img/rl.png"))
        self.images.append(pygame.image.load("img/rr.png"))
        self.images.append(pygame.image.load("img/ml.png"))
        self.images.append(pygame.image.load("img/mr.png"))
        self.images.append(pygame.image.load("img/fl.png"))
        self.images.append(pygame.image.load("img/fr.png"))
        self.images.append(pygame.image.load("img/disabled.png"))
        self.images.append(pygame.image.load("img/enabled.png"))

    def defineInterface(self):
        self.selection = 0
        self.buttons = []

        #Limb selection buttons mapping
        self.buttons.append(pygame.Rect(91,133,74,55)) #No limb
        self.buttons.append(pygame.Rect(34,68,69,77))
        self.buttons.append(pygame.Rect(32,183,69,68))
        self.buttons.append(pygame.Rect(107,52,57,78))
        self.buttons.append(pygame.Rect(104,186,57,83))
        self.buttons.append(pygame.Rect(156,90,62,48))
        self.buttons.append(pygame.Rect(153,182,62,53))

        #Shutdown    
        self.buttons.append(pygame.Rect(415,256,41,41))

        #Limb control buttons mapping
        self.buttons.append(pygame.Rect(260,205,41,41))
        self.buttons.append(pygame.Rect(301,205,41,41))
        self.buttons.append(pygame.Rect(342,205,41,41))
        self.buttons.append(pygame.Rect(397,205,41,41))

    def drive(self, servo, pos):
        cmd = "#%d P%d\r" % (servo, pos)
        self.port.write(cmd)

    def __init__(self):
        self.initDisplay()
        self.loadResources()
        self.defineInterface()
        
        self.port = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=115200
        )
        # Future controller support
        # self.robotController = XboxController.XboxController(
        #     controllerCallBack = None,
        #     joystickNo = 0,
        #     deadzone = 0.1,
        #     scale = 1,
        #     invertYAxis = False)

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

    #Controller support to be added later
    def ctrlCallback(ctrlId, val):
        print "Control id = {}, Value = {}".format(ctrlId, val)

    #Redraw GUI
    def drawGui(self):
        self.screen.blit(self.images[0], (0,0))

        font = pygame.font.SysFont("monospace", 11)
        label = font.render(self.limbs[self.selection] + " limb selected", 1, (255,255,255))
        
        if self.selection != 0 and self.selection <= 6:
            self.screen.blit(self.images[self.selection], self.buttons[self.selection])
            self.screen.blit(self.images[8], (260,205))
        elif self.selection == 7:
            self.run = False
        else:
            self.screen.blit(self.images[7], (260,205))

        self.screen.blit(label, (250, 185))
        # Update the display
        pygame.display.update()

    #Handle user input
    def clickEvent(self, pos):
        for i, b in enumerate(self.buttons):
            if b.collidepoint(pos):
                if i in range(0,8):
                    self.selection = i;
                elif i == 8 and self.selection in range(1,6):
                    self.drive(self.selection-1, 1900)
                elif i == 9 and self.selection in range(1,6):
                    self.drive(self.selection-1, 1100)
                elif i == 10 and self.selection in range(1,6):
                    self.drive(self.selection-1, 1500)

# Create an instance of the PyScope class
fw = htf()
#gui.controller.start()
run = 1
fw.port.open()
while fw.run: 
    fw.drawGui()
    time.sleep(0.1)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                #run = 0
                fw.clickEvent(pygame.mouse.get_pos())
                break
#gui.controller.stop()

fw.port.close()
