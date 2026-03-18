#Other class creation for interfacing with components
from machine import Pin, PWM
from utime import sleep

class Motor:           #class used for control of motor components
    def __init__(self, dirPin, PWMPin):
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
        
    def off(self):
        self.pwm.duty_u16(0)   #turns off Motor
        
    def Forward(self, speed=100):
        self.mDir.value(0)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor

    def Reverse(self, speed=30):
        self.mDir.value(1)
        self.pwm.duty_u16(int(65535 * speed / 100))
        
    def set_speed(self, speed=100):               #inputs single set speed function that sets motor into forward or reverse
        if speed > 0 and speed <= 100:
            self.Forward(speed)
        elif speed < 0 and speed >= -100:
            self.Reverse(-speed)
        elif speed == 0:
            self.off()
        else:
            pass
        
class Servo:          #class used for control of servo components
    def __init__(self, PWMPin, rotation = 0):
        self.pwm_pin = PWM(Pin(PWMPin), 50)
        self.min = 1638                 #sets the min and max values repesenting 0 and 270 degrees respectively 
        self.max = 8191
        self.rotation = rotation
        
           
    def setrotation(self, rotation):      #moves servo to desired angle input 
        rotation = max(0,min(270,rotation))
        self.rotation = rotation       
        u16_level = int((rotation/270)*(self.max-self.min)+ self.min)   #linearly interpolates to move servo to desired angle
        self.pwm_pin.duty_u16(u16_level)
        sleep(0.02)
    

class Optocoupler:                              #groups line sensor inputs into single class
    def __init__(self, OuterL, OuterR, InnerL, InnerR):
        self.OuterL = Pin(OuterL, Pin.IN, Pin.PULL_DOWN)     #outer left hand sensor 
        self.OuterR = Pin(OuterR, Pin.IN, Pin.PULL_DOWN)    #outer right hand sensor
        self.InnerL = Pin(InnerL, Pin.IN, Pin.PULL_DOWN)    #inner left hand sensor
        self.InnerR = Pin(InnerR, Pin.IN, Pin.PULL_DOWN)    #inner right hand sensor
        
        
    def getvalues(self):
        values = [self.OuterL.value(), self.OuterR.value(), self.InnerL.value(), self.InnerR.value()]
        return values
    
    def read_line(self):
        return self.InnerL.value(), self.InnerR.value()

    def read_junction(self):
        return self.OuterL.value(), self.OuterR.value()
    
    def junction_detection(self):    #determines whether a junction has been detected each time the system updates
        
        if (self.OuterL.value() == 1) or (self.OuterR.value() == 1):
            return 'JUNCTION'
            
        else:
            return 'CLEAR'

        
        

