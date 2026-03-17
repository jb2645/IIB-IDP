#Other class creation for interfacing with components
from machine import Pin, PWM

class Motor:
    def __init__(self, dirPin, PWMPin):
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
        
    def off(self):
        self.pwm.duty_u16(0)
        
    def Forward(self, speed=100):
        self.mDir.value(0)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor

    def Reverse(self, speed=30):
        self.mDir.value(1)
        self.pwm.duty_u16(int(65535 * speed / 100))
        
    def set_speed(self, speed=100):               #combines previous functions into single set speed function that sets motor into forward or reverse
        if speed > 0 and speed <= 100:
            self.Forward(speed)
        elif speed < 0 and speed >= -100:
            self.Reverse(-speed)
        elif speed == 0:
            self.off()
        else:
            print("Invalid motor speed input")
        
class Servo:                                 #defines servo class for controlling any actuators in the design
        self.pwm_pin = PWM(Pin(PWMPin), 50)
        self.min = 1638
        self.max = 8191
        
           
    def setrotation(self, rotation):
    

class Optocoupler:                              #groups optocouple sensor inputs into single class
    def __init__(self, OuterL, OuterR, InnerL, InnerR):
        self.OuterL = Pin(OuterL, Pin.IN, Pin.PULL_DOWN)     #outer left hand sensor 
        self.OuterR = Pin(OuterR, Pin.IN, Pin.PULL_DOWN)
        self.InnerL = Pin(InnerL, Pin.IN, Pin.PULL_DOWN)
        self.InnerR = Pin(InnerR, Pin.IN, Pin.PULL_DOWN)
        
        
    def getvalues(self):
        values = [self.OuterL.value(), self.OuterR.value(), self.InnerL.value(), self.InnerR.value()]
        #print(values)
        return values
    
    def read_line(self):
        return self.InnerL.value(), self.InnerR.value()

    def read_junction(self):
        return self.OuterL.value(), self.OuterR.value()
    
    def junction_detection(self):    #determins whether a detected junction is a node or a turning
        
        if (self.OuterL.value() == 1) or (self.OuterR.value() == 1):
            return 'JUNCTION'
            
        else:
            return 'CLEAR'

        
        

