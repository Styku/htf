from Leg import Leg

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