#Rover class definitions

#import voltagefetcher

class Rover:
    def __init__(self, motorL, motorR):
        self.left = motorL
        self.right = motorR
        self.testvoltagein = 0
        
        #define all other sensors when decided
        
        

    def getTestVoltage(self):
        return self.testvoltagein
    
    def DetermineColour(self):
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
        
    def pickup(self):
        
        colour = Determinecolour()
        
    def putdown(self):
        
    def moveforward(self):
    
    def turnleft(self):
        
    def turnright(self):
        
    
        
    
        
        
        
        
        
    