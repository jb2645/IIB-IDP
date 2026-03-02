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
        
class Actuator:
    def __init__(self, dirPin, PWMPin):
        self.mDir = Pin(dirPin, Pin.OUT)  # set motor direction pin
        self.pwm = PWM(Pin(PWMPin))  # set motor pwm pin
        self.pwm.freq(1000)  # set PWM frequency
        self.pwm.duty_u16(0)  # set duty cycle - 0=off
           
    def set(self, dir, speed):
        self.mDir.value(dir)                     # forward = 0 reverse = 1 motor
        self.pwm.duty_u16(int(65535 * speed / 100))  # speed range 0-100 motor

class Optocoupler:
    def __init__(self, OuterL, OuterR, InnerL, InnerR):
        self.OuterL = Pin(OuterL, Pin.IN, Pin.PULL_DOWN)
        self.OuterR = Pin(OuterR, Pin.IN, Pin.PULL_DOWN)
        self.InnerL = Pin(InnerL, Pin.IN, Pin.PULL_DOWN)
        self.InnerR = Pin(InnerR, Pin.IN, Pin.PULL_DOWN)
        
        
    def getvalues(self):
        values = [self.OuterL.value(), self.OuterR.value(), self.InnerL.value(), self.InnerR.value()]
        return values
    
    def read_line(self):
        return self.InnerL.value(), self.InnerR.value()

    def read_junction(self):
        return self.OuterL.value(), self.OuterR.value()
    
    def junction_detection(self):
        
        if (self.OuterL == 1) or (self.OuterR == 1):
            if (self.InnerL ==0) and (self.InnerR==0):
                return 'TURN'
                
            else:
                return 'NODE'
            
        else:
            return 'CLEAR'

        
        

