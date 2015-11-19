from Joint import Joint

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