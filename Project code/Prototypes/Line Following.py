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


class Position:
    def __init__():
        self.row = row #[(0,1,2,3);(0,1,2,3)]  0->1,3  1->0,2 2->1,3,R 
        self.heading = heading  #[N,E,S,W]
        self.node = node
        self.turn = turn
        
    def on_node(self):
        if self.heading == 0 or self.heading==3: # 0=North 3=West
            self.node+=1
            
        elif self.heading==1 or self.heading ==2: # 1=East  2=South
            self.node-=1
            
    def on_turn_end(self):
        if self.turn == 0: #right
            self.heading = (self.heading+1)%4
            
            
        elif self.turn == 1: #left
            self.heading = (self.heading-1)%4
            
            
    def on_turn_node(self):
        pass
    

def main():
    
    left_motor = Motor(dirPin=4, PWMPin=5)#check values later
    right_motor = Motor(dirPin=6, PWMPin=7)
    
 #   drive = MainDrive(left_motor, right_motor)
    drive = Rover(left_motor, right_motor) # This will need to be updated later when rover class completed
    
    
    #sensors = LineSensors(['''pin1,pin2,pin3,pin4'''])
    sensors = Optocoupler(6, 7, 8, 9)      #check actual order of gpio pins
    
    follower = LineFollow(drive, sensors)
    
    while True:
        state = sensors.junction_detection()
        active = follower.update()
        
        if state!='CLEAR':
            if state=='NODE':
                #position initalisation
                
            elif state=='TURN':
                left_value, right_value = sensors.read_junction()
                
                if left_value>right_value:
                    #turn left
                    
                else:
                    #turn right 
        
        time.sleep(0.01)