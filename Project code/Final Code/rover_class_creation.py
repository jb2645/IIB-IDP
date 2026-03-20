#Rover class definitions
from machine import Pin, ADC
from general_component_classes import *

from utime import sleep
from machine import Pin, I2C

from libs.tcs3472_micropython.tcs3472 import tcs3472
from libs.VL53L0X.VL53L0X import VL53L0X

#from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701    #shouldnt have this sensor?

class Rover:
    def __init__(self, motorR, motorL, Optocoupler, horizontalservo, verticalservo, isholdingblock = False):
        self.left = motorL
        self.right = motorR
        self.testvoltagein = 0
        self.Optocoupler = Optocoupler
        self.blueled = Pin(11, Pin.OUT)    
        self.greenled = Pin(10, Pin.OUT)
        self.redled = Pin(9, Pin.OUT)
        self.yellowled = Pin(8, Pin.OUT)
        self.isholdingblock = isholdingblock   #determines whether grabber is carrying a block
        self.horizontalservo = horizontalservo
        self.verticalservo = verticalservo
        self.frontvl53l0 = 0
        self.rightvl53l0 = 0
        self.VL53INIT()    #initialise distance sensors
        
        
    def VL53INIT(self):
        fronti2c_bus = I2C(id=1, sda=Pin(18), scl=Pin(19), freq=100000)    #sets I2C pins used for sensors
        
        sleep(0.05)
        
        self.frontvl53l0 = VL53L0X(fronti2c_bus)
        self.frontvl53l0.set_Vcsel_pulse_period(self.frontvl53l0.vcsel_period_type[0], 18)  
        self.frontvl53l0.set_Vcsel_pulse_period(self.frontvl53l0.vcsel_period_type[1], 14)
        self.frontvl53l0.start()

        righti2c_bus = I2C(id=0, sda=Pin(16), scl=Pin(17), freq=100000) 

        sleep(0.05)
        
        self.rightvl53l0 = VL53L0X(righti2c_bus)
        self.rightvl53l0.set_Vcsel_pulse_period(self.rightvl53l0.vcsel_period_type[0], 18)      
        self.rightvl53l0.set_Vcsel_pulse_period(self.rightvl53l0.vcsel_period_type[1], 14)
        self.rightvl53l0.start()
        
        
    def getDistance(self, direction):
        # Determine which direction of sensor is being activated, return relevant sensor input 
        if direction == "R":
            distance = self.rightvl53l0.read()
            
        if direction == "F":
            distance = self.frontvl53l0.read()
        return distance
        
    def deployGrabber(self): #moves grabber arm down 
        self.verticalservo.setrotation(15)
        
    def setvert(self, num):  #moves grabber arm to specific vertical position  - redundant
        self.verticalservo.setrotation(num)

    def stowGrabber(self): #move grabber arm up to vertical position
        self.verticalservo.setrotation(80)
        
    def raiseGrabber(self): #moves grabber arm up slightly to move block out of bay
        self.verticalservo.setrotation(20)
        
    def grab(self): #moves horziontal arm of grabber to grab block
        self.horizontalservo.setrotation(90)
        
    def release(self): #moves horizontal arm to release block
        self.horizontalservo.setrotation(55)
        
    def SetBlockStatus(self, isholdingblock):
        self.isholdingblock = isholdingblock
        
    def GetBlockStatus(self):
        return self.isholdingblock
        
    def pickup(self): #deploys grabbing arm to pick up block
        self.isholdingblock = True
        sleep(0.2)
        self.release()
        sleep(1)          
        self.deployGrabber()
        sleep(1)          
        self.grab()
        sleep(1)         
        self.raiseGrabber()
        sleep(1)          
        
        
    def putdown(self): #deploys grabbing arm to put down block
        self.blueled.value(0)       #switch off all LEDs
        self.greenled.value(0)
        self.redled.value(0)
        self.yellowled.value(0)
        self.isholdingblock = False
        
        self.deployGrabber()   #places block down
        sleep(0.3)
        self.release()
        sleep(0.4)
        self.stowGrabber()
        self.grab()
        
    
    def drive(self, left_speed, right_speed):
        self.left.set_speed(left_speed)
        self.right.set_speed(right_speed)

    def stop(self):
        self.left.off()
        self.right.off()

    def getTestVoltage(self):
        return self.testvoltagein
    
    def DetermineColour(self):
        #determined voltages = 0.05 blue , 0.38 green, 1.84 red, 2.19 yellow
        adc = ADC(26)    # sets GPIO 26 as analogue port in
        valuein = adc.read_u16()      
        testvoltagein = valuein * 3.3 / 65535           #converts analogue signal to voltage
        self.testvoltagein = testvoltagein

        #determine colour based on input voltage range and switches on relevant LED
        if self.testvoltagein > 0.01 and self.testvoltagein < 0.1:
            self.blueled.value(1)
            return "Blue"
        elif self.testvoltagein > 0.2 and self.testvoltagein < 0.6:
            self.greenled.value(1)
            return "Green"
        elif self.testvoltagein > 1.4 and self.testvoltagein < 2.0:
            self.redled.value(1)
            return "Red"
        elif self.testvoltagein > 2.1 and self.testvoltagein < 2.21:
            self.yellowled.value(1)
            return "Yellow"
        else:
            return "None"        
        
    def turnleft(self): 
        self.right.Forward(85)
        self.left.Reverse(75)
        sleep(0.5)  #Sleep to ensure does not recognise it has finished turn too early
        turning = True
        while turning: # will keep turning until both line sensors have detected new line
            sensorvalues = self.Optocoupler.getvalues()
            if sensorvalues[3] == 1:
                self.stop()
                turning = False
                
    def turnright(self):
        self.left.Forward(85)
        self.right.Reverse(75)
        sleep(0.5)
        turning = True
        while turning:
            sensorvalues = self.Optocoupler.getvalues()
            if sensorvalues[2] == 1:
                self.stop()
                turning = False

        
    def blockturnleft(self):   #slightly modified turning functions for turning out of bays
        self.right.Forward(85)
        self.left.Reverse(75)
        sleep(0.6)
        turning = True
        while turning:
            sensorvalues = self.Optocoupler.getvalues()
            if sensorvalues[3] == 1:
                self.stop()
                turning = False
        
    def blockturnright(self): #slightly modified turning functions for turning out of bay
        self.left.Forward(85)
        self.right.Reverse(75)
        sleep(0.6)
        turning = True
        while turning:
            sensorvalues = self.Optocoupler.getvalues()
            if sensorvalues[2] == 1:
                self.stop()
                turning = False        
    

    def RightUTurn(self): #Function for rover to perfor a U-turn turning right
        turning= True
        self.left.Forward(100)
        self.right.Reverse(100)
        sleep(0.5)
        while turning:   #stops turning when inner left line sensor detects line again 
            sensorvalues = self.Optocoupler.getvalues()
            if sensorvalues[2] == 1:
                self.stop()
                turning = False    

        
    def LeftUTurn(self):  #Function for rover to perfor a U-turn turning left
        turning = True
        self.right.Forward(100)
        self.left.Reverse(100)
        sleep(0.5)
        while turning: #stops turning when inner right line sensor detects line again 
            sensorvalues = self.Optocoupler.getvalues()
            if sensorvalues[3] == 1:
                self.stop()
                turning = False
        
    def reverseright(self): #reverses rover backwards out of a bay - redundant
        self.right.Forward(75)
        self.left.Reverse(85)
        sleep (0.8)
        self.stop()

    def reverseleft(self): #reverses rover backwards out of a bay - redundant
        self.left.Forward(75)
        self.right.Reverse(85)
        sleep (0.8)
        self.stop()
            
            
    def drive_onto_junction(self, duration=0.23):   #moves rover slightly ahead of junction after it has been detected
        self.drive(80, 80)
        sleep(duration)
        self.stop()

       

    
        
    
        
    
        
        
        
        
        
    