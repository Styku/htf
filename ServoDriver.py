import serial

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