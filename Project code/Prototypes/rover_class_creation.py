#Rover class definitions
from machine import Pin, ADC
from general_component_classes import *

from utime import sleep
from machine import Pin, SoftI2C, I2C

from libs.tcs3472_micropython.tcs3472 import tcs3472
from libs.VL53L0X.VL53L0X import VL53L0X

#from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701    #shouldnt have this sensor?

class Rover:
    def __init__(self, motorR, motorL, Optocoupler, horizontalservo, verticalservo, isholdingblock = False):
        self.state = "Travel"
        self.left = motorL
        self.right = motorR
        self.testvoltagein = 0
        self.Optocoupler = Optocoupler
        self.blueled = Pin(11, Pin.OUT)
        self.greenled = Pin(10, Pin.OUT)
        self.redled = Pin(9, Pin.OUT)
        self.yellowled = Pin(8, Pin.OUT)
        self.isholdingblock = isholdingblock
        self.horizontalservo = horizontalservo
        self.verticalservo = verticalservo
        self.frontvl53l0 = 0
        self.rightvl53l0 = 0
        self.VL53INIT()
        
        
    def VL53INIT(self):
        fronti2c_bus = I2C(id=0, sda=Pin(16), scl=Pin(17))    #sets I2C pins used for sensors
        #righti2c_bus = I2C(id=0, sda=Pin(18), scl=Pin(19))
        
        self.frontvl53l0 = VL53L0X(fronti2c_bus)
        self.frontvl53l0.set_Vcsel_pulse_period(self.frontvl53l0.vcsel_period_type[0], 18)      #sets pulse period/range of sensor
        self.frontvl53l0.set_Vcsel_pulse_period(self.frontvl53l0.vcsel_period_type[1], 14)
        self.frontvl53l0.start()
        
        #self.rightvl53l0 = VL53L0X(righti2c_bus)
        #self.rightvl53l0.set_Vcsel_pulse_period(self.rightvl53l0.vcsel_period_type[0], 18)      #sets pulse period/range of sensor
        #self.rightvl53l0.set_Vcsel_pulse_period(self.rightvl53l0.vcsel_period_type[1], 14)
        #self.rightvl53l0.start()
        
        
    def getDistance(self, direction):
        # Determine which direction of sensor is being activated
        #if direction == "R":
            #distance = self.rightvl53l0.read()
            
        if direction == "R":
            distance = self.frontvl53l0.read()
            
        return distance
        
    def deployGrabber(self):
        self.verticalservo.setrotation(20)

    def stowGrabber(self):
        self.verticalservo.setrotation(90)

        
    def SetBlockStatus(self, isholdingblock):
        self.isholdingblock = isholdingblock
        
    def GetBlockStatus(self):
        return self.isholdingblock
        
    def drive(self, left_speed, right_speed):
        self.left.set_speed(left_speed)
        self.right.set_speed(right_speed)

    
    def For(self):
        self.left.Forward()

    def stop(self):
        self.left.off()
        self.right.off()

    def getTestVoltage(self):
        return self.testvoltagein
    
    def DetermineColour(self):
        #expected voltages for given resistances - 0.029 - 100 ohm, 0.273 1kohm, 1.5 10kohm, 2.727 100kohm   ####change this later
        adc = ADC(26)    # sets GPIO 26 as analogue port in
        valuein = adc.read_u16()      
        testvoltagein = valuein * 3.3 / 65535           #converts analogue signal to voltage
        self.testvoltagein = testvoltagein
        if self.testvoltagein > 0.02 and self.testvoltagein < 0.04:
            self.blueled.value(1)
            return "Blue"
        elif self.testvoltagein > 0.2 and self.testvoltagein < 0.4:
            self.greenled.value(1)
            return "Green"
        elif self.testvoltagein > 1.4 and self.testvoltagein < 1.6:
            self.redled.value(1)
            return "Red"
        elif self.testvoltagein > 2.65 and self.testvoltagein < 2.95:
            self.yellowled.value(1)
            return "Yellow"
        else:
            print("No Object")
            return "None"
        
    def pickup(self):
        self.isholdingblock = True
        self.horizontalservo.setrotation(110)
        self.verticalservo.setrotation(5)
        sleep(0.1)
        self.horizontalservo.setrotation(80)
        self.drive(-45, -45)
        sleep(0.1)
        self.verticalservo.setrotation(90)
        
        
    def putdown(self):
        self.blueled.value(0)       #switch off all LEDs
        self.greenled.value(0)
        self.redled.value(0)
        self.yellowled.value(0)
        self.isholdingblock = False
        
        
        
    
    
    def turnleft(self):
        self.right.Forward(85)
        self.left.Reverse(75)
        sleep (0.8)
        self.stop()
        
    def turnright(self):
        self.left.Forward(85)
        self.right.Reverse(75)
        sleep (0.8)
        self.stop()
        
    def blockturnleft(self):
        self.right.Forward(85)
        self.left.Reverse(75)
        sleep (0.7)
        self.stop()
        
    def blockturnright(self):
        self.left.Forward(85)
        self.right.Reverse(75)
        sleep (0.7)
        self.stop()        
    

    def RightUTurn(self):
        turned = False
        self.left.Forward(85)
        self.right.Reverse(85)
        sleep (1.35)
        self.stop()
        
    def LeftUTurn(self):
        turned = False
        self.right.Forward(85)
        self.left.Reverse(85)
        sleep (1.35)
        self.stop()

    def motortest(self):
        print("Test")
        self.right.Forward(75)
        sleep(2)
        self.stop()
        self.left.Forward(75)
        sleep(2)
        self.stop()
        
        #self.left.Forward(75)
        
    def reverseright(self):
        self.right.Forward(75)
        self.left.Reverse(85)
        sleep (0.8)
        self.stop()

    def reverseleft(self):
        self.left.Forward(75)
        self.right.Reverse(85)
        sleep (0.8)
        self.stop()
    
    def reverseleft1(self):
        turned = False
        motorstarted = False
        slowflag = False
        nearlyturned = False
        
        while turned == False:
            #self
            if slowflag == False and motorstarted == False:
                self.right.Forward(75)
                self.left.Reverse(75)
                motorstarted = True
            
            ###Test to verify which way round sensor detection needs to work
            sensorvalues = self.Optocoupler.getvalues()          #finds the sensor values
            
            if sensorvalues[0] == 1:                   #slows down turn when outer sensor detects line desired 
                if slowflag == False:
                    sleep(0.08)
                    slowflag = True
                    self.right.Forward(60)
                    self.left.Reverse(60)
        
            if sensorvalues[2] == 1:#to discard any anomalous readins in LH sensor
                sleep(0.1)
                nearlyturned = True
                
            if sensorvalues[3] == 1 and sensorvalues[1] == 0 and nearlyturned == True:
                sleep(0.2)
                turned = True
                
    def reverseright1(self):
        turned = False
        motorstarted = False
        slowflag = False
        nearlyturned = False
        
        while turned == False:
            #self
            if slowflag == False and motorstarted == False:
                self.left.Forward(75)
                self.right.Reverse(75)
                motorstarted = True
            
            sensorvalues = self.Optocoupler.getvalues()          #finds the sensor values
            
            if sensorvalues[0] == 1:                   #slows down turn when outer sensor detects line desired 
                if slowflag == False:
                    sleep(0.08)
                    slowflag = True
                    self.left.Forward(60)
                    self.right.Reverse(60)
        
            if sensorvalues[2] == 1:#to discard any anomalous readins in LH sensor
                sleep(0.1)
                nearlyturned = True
                
            if sensorvalues[3] == 1 and sensorvalues[1] == 0 and nearlyturned == True:
                sleep(0.2)
                turned = True
                
            #sleep(0.05)
            
            
    def drive_onto_junction(self, duration=0.23):
        self.drive(80, 80)
        sleep(duration)
        self.stop()

       

    
        
    
        
    
        
        
        
        
        
    