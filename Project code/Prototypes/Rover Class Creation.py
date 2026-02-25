#Rover class definitions
from machine import Pin
from "General Component Classes.py" import *

class Rover:
    def __init__(self, motorL, motorR):
        self.left = motorL
        self.right = motorR
        self.testvoltagein = 0
        
        #define all other sensors when decided
        
    def drive(self, left_speed, right_speed):
        self.left.set_speed(left_speed)
        self.right.set_speed(right_speed)

    def stop(self):
        self.left.stop()
        self.right.stop()

    def getTestVoltage(self):
        return self.testvoltagein
    
    def DetermineColour(self):
        VinPin = Pin(26, Pin.IN)       #fetch tested voltage value from GPIO pin 26
        testvoltagein = VinPin.value()
        #expected voltages for given resistances - 0.029 - 100 ohm, 0.273 1kohm, 1.5 10kohm, 2.727 100kohm
        self.testvoltagein = testvoltagefetch()
        if self.testvoltagein > 0.02 and self.testvoltagein < 0.04:
            return "Blue"
        elif self.testvoltagein > 0.2 and self.testvoltagein < 0.4:
            return "Green"
        elif self.testvoltagein > 1.4 and self.testvoltagein < 1.6:
            return "Red"
        elif self.testvoltagein > 2.65 and self.testvoltagein < 2.95:
            return "Yellow"
        else:
            print("No Object")
            return "None"
        
    def pickup(self):
        
        colour = Determinecolour()
        
    def putdown(self):
        
    def moveforward(self):
    
    def turnleft(self):
        
    def turnright(self):
        
    
        
    
        
        
        
        
        
    