#Rover class definitions
from machine import Pin, ADC
from "Project code\Prototypes\general_component_classes.py" import *

from utime import sleep
from machine import Pin, SoftI2C, I2C

from libs.tcs3472_micropython.tcs3472 import tcs3472

#from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701    #shouldnt have this sensor?

class Rover:
    def __init__(self, motorL, motorR, Optocoupler):
        self.state = "Travel"
        self.left = motorL
        self.right = motorR
        self.testvoltagein = 0
        self.Optocoupler = Optocoupler
        
        #define all other sensors when decided
        
    def SensingState(self):
        self.state = "Sensing"
        
    def TravelState(self):
        self.state = "Travel"
        
    def PickupState(self):
        self.state = "Pickup"
        
    def GetRoverState(self):
        return self.state
        
    def drive(self, left_speed, right_speed):
        self.left.set_speed(left_speed)
        self.right.set_speed(right_speed)

    def stop(self):
        self.left.stop()
        self.right.stop()

    def getTestVoltage(self):
        return self.testvoltagein
    
    def DetermineColour(self):
        #expected voltages for given resistances - 0.029 - 100 ohm, 0.273 1kohm, 1.5 10kohm, 2.727 100kohm   ####change this later
        adc = ADC(26)    # sets GPIO 26 as analogue port in
        valuein = adc.read_u16()      
        testvoltagein = valuein * 3.3 / 65535           #converts analogue signal to voltage
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
        #linefollow until within 1cm
        while self.getDistance("F") > 1:    #value to be determined later 
            self.linefollow()

        
        colour = self.Determinecolour()
        return colour
        #if colour == "Blue":
        #    destination =
        
        
    def putdown(self):
        
    def moveforward(self):
    
    def turnleft(self):
        turned = False
        while turned == False:
            self.left.Foward(50)
            self.right.reverse(20)   #adjust values later
            sensorvalues = self.Optocoupler.getvalues()
            if sensorvalues == [0, 0, 1, 1]:   #redefine as an interrupt
                turned = False
    def turnright(self):
            def turnleft(self):
            turned = False
            while turned == False:
                self.left.Foward(50)
                self.right.reverse(20)   #adjust values later
                sensorvalues = self.Optocoupler.getvalues()
                if sensorvalues == [0, 0, 1, 1]:
                    turned = False


        
        
        
        
    def getDistance(self, direction):
        VL53 = False
        # Determine which direction of sensor is being activated
        if direction == "F":
            i2c_bus = I2C(id=0, sda=Pin(10), scl=Pin(11)) # Left hand Sensor attached to GPIO 8, 9
            VL53 = True
            
        if direction == "R":
            i2c_bus = I2C(id=0, sda=Pin(16), scl=Pin(17)) # Right hand Sensor attached to GPIO 
            VL53 = True
            
        if VL53:
            # print(i2c_bus.scan())  # Get the address (nb 41=0x29, 82=0x52)    - shouldnmt be neccessary
            
            # Setup vl53l0 object
            vl53l0 = VL53L0X(i2c_bus)
            vl53l0.set_Vcsel_pulse_period(vl53l0.vcsel_period_type[0], 18)      #sets pulse period/range of sensor
            vl53l0.set_Vcsel_pulse_period(vl53l0.vcsel_period_type[1], 14)

            vl53l0.start()    
            distance = vl53l0.read()           #if inaccurate in testing then take multiple data points and average. 
            
            # Stop device
            vl53l0.stop()
            
            return distance
            
        else:
            #put in code for Ultrasonic sensor here
                        
                        #define  MAX_RANG      (520)//the max measurement vaule of the module is 520cm(a little bit longer than  effective max range)
            #define  ADC_SOLUTION      (1023.0)//ADC accuracy of Arduino UNO is 10bit

            import sys
            import time

            import URM09

            #sys.path.append("../..")
            ''' Create a URM09 object to communicate with I2C. '''
            URM09 = URM09.DFRobot_URM09()
            ''' Set the i2c device number '''
            URM09.begin(0x11)     #find out i2c bus address 
            
            URM09.SetModeRange(URM09._MEASURE_MODE_PASSIVE, URM09._MEASURE_RANG_500)
            while(1):
                ''' Write command register and send ranging command '''
                URM09.SetMeasurement()
                time.sleep(0.1)
                ''' Read distance register '''
                distance = URM09.i2cReadDistance()
                
                return distance
                ''' Read temperature register '''
                temp = URM09.i2cReadTemperature()

    
        
    
        
    
        
        
        
        
        
    