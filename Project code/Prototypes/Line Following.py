from machine import Pin, PWM
import time


from "General Component Classes.py" import *
from "Rover Class Creation.py" import 

 


#class Motor: #Motor setup
#    def __init__(self, pwm_pin, dir_pin):
#        self.pwm = PWM(Pin(pwm_pin))
#        self.dir = Pin(dir_pin, Pin.OUT)
#        self.pwm.freq(1000)
#    
#    def set_speed(self, speed):
#        
#        speed = max(min(speed,100),-100)
#        
#        if speed >= 0:
#            self.dir.value(1)
#        else:
#            self.dir.value(0)
#        
#        duty = int(abs(speed)*655)
 #       self.pwm.duty_u16(duty)
 #       
 #   def stop(self):
 #       self.pwm.duty_u16(0)
        
#class MainDrive:
#    def __init__(self, left_motor, right_motor):
#        self.left = left_motor
#        self.right = right_motor
        
##    def drive(self, left_speed, right_speed):
#        self.left.set_speed(left_speed)
#        self.right.set_speed(right_speed)

 #   def stop(self):
  #      self.left.stop()
   #     self.right.stop()

class LineSensors:
    def __init__(self,fleft_pin,left_pin,right_pin,fright_pin):
        self.fleft = fleft_pin
        self.left = left_pin
        self.right = right_pin
        self.fright = fright_pin
        
    
    def read_line(self):
        return self.left.value(), self.right.value()

    def read_junction(self):
        return self.fleft.value(), self.fright.value()
        
    
    def junction_detection(self):
        fl,fr = self.read_junction()
        l,r = self.read_line()
        state = 'CLEAR'
        
        if (fl==1) or (fr==1):
            if (l==0) and (r==0):
                state = 'TURN'
                return state
                
            else:
                state = 'NODE'
                return state
                
            
        

class LineFollow:
    def __init__(self, drive, sensors, base_speed=40, correction=20):
        self.drive = drive
        self.sensor = sensors
        self.base_speed = base_speed
        self.correction = correction
        self.last_direction = 0
        
    def update(self):
        left, right = self.sensors.read_line()
        
        l = 0
        r = 0
        direction = 0
        
        if left>right:
            l = -1
            r = 1
            direction = -1
        elif left<right:
            l = 1
            r = -1
            direction = 1
        
        self.drive.drive(self.base_speed + l * self.correction, self.base_speed + r * self.correction)
        self.last_direction = 0
        
    left_speed = self.base_speed - correction
    right_speed = self.base_speed + correction
    
    self.drive.drive(left_speed,right_speed)
    return active

def main():
    
    left_motor = Motor('''pwm pin, direction pin''')
    right_motor = Motor('''pwm pin, direction pin''')
    
 #   drive = MainDrive(left_motor, right_motor)
     drive = Rover(left_motor, right_motor) # This will need to be updated later when rover class completed

    sensors = LineSensors(['''pin1,pin2,pin3,pin4'''])
    
    follower = LineFollow(drive, sensors)
    
    while True:
        state = sensors.junction_detection()
        active = follower.update()
        
        if state!='CLEAR':
            if state=='NODE':
                #position initialisation
            elif state=='TURN':
                left_value, right_value = sensors.read_junction()
        
        time.sleep(0.01)