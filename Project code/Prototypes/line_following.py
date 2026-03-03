from machine import Pin, PWM
import time

from general_component_classes import *
from rover_class_creation import * 
        
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
        self.fleft = Pin(fleft_pin,Pin.IN)
        self.left = Pin(left_pin,Pin.IN)
        self.right = Pin(right_pin,Pin.IN)
        self.fright = Pin(firght_pin,Pin.IN)
        
    
    def read_line(self):
        return self.left.value(), self.right.value()

    def read_junction(self):
        return self.fleft.value(), self.fright.value()
        
    def get_event(self):
        fl,fr = self.read_junction()
        l,r = self.read_line()
        
        if (fl==1) or (fr==1):
            if (l==0) and (r==0):
                return "TURN"
                
            else:
                return "NODE"
            
        else:
            return "CLEAR"
                
            
        

class LineFollow:
    def __init__(self, drive, sensors, base_speed=80, correction=20):
        self.drive = drive
        self.sensors = sensors
        self.base_speed = base_speed
        self.correction = correction
        
    def adjust(self):
        left, right = self.sensors.read_line()
        
        if left == 0 and right == 0:
            self.drive.drive(self.base_speed, self.base_speed)

        elif left == 1 and right == 0:
            self.drive.drive(self.base_speed - self.correction,
                             self.base_speed + self.correction)

        elif left == 0 and right == 1:
            self.drive.drive(self.base_speed + self.correction,
                             self.base_speed - self.correction)
        
        else:
            self.drive.drive(self.base_speed, self.base_speed)


class Position:
    def __init__(self,grid):
        self.grid = grid #((3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(x,5),(x,5))
        self.row = 0
        self.heading = 0  #[N,E,S,W]
        self.node = 2
        self.state = "CLEAR"
        
    def update(self,event):
        self.state = event
        
    def find_row(self):
        if self.heading == 0 or self.heading == 1:
            return self.grid[self.row][0]
        
        if self.heading == 2 or self.heading == 3:
            return self.grid[self.row][1]
     
    def on_node(self, case='NORMAL'):
        if case=='NORMAL':
            if self.heading == 0 or self.heading==3: # 0=North 3=West
                self.node+=1
            
            elif self.heading==1 or self.heading ==2: # 1=East  2=South
                self.node-=1

            
            
    def turn_end(self,turn):
        self.row = self.find_row()
        
        if turn == 0: #right
            self.heading = (self.heading+1)%4
            
            
        elif turn == 1: #left
            self.heading = (self.heading-1)%4
        
            
            
    def turn_node(self):
        if self.node == 6:
            pass
    

class Path_LFT:
    def __init__(self, drive, sensors):
        self.drive = drive
        self.sensors = sensors

        self.state = "LEAVING_START"
        self.turn_count = 0

    def update(self):

        event = self.sensors.junction_detection()

        if self.state == "LEAVING_START":
            # Follow until first turn
            if event == "TURN":
                self.drive.turn_left()
                self.state = "OUTER_LOOP"

        elif self.state == "OUTER_LOOP":
            if event == "TURN":
                self.turn_count += 1
                self.drive.turn_right()

                if self.turn_count == 4:
                    self.state = "RETURNING"

        elif self.state == "RETURNING":
            if event == "NODE" and self.pos.node == 2:
                self.drive.turn_left()
                self.state = "STOP"

        elif self.state == "STOP":
            self.drive.stop()


def SensingInterrupt():
    if drive.GetRoverState() == "Sensing":
        OuterSensorGPIOnum = 9
        OuterSensor = Pin(OuterSensorGPIOnum, Pin.IN, Pin.PULL_DOWN)
        OuterSensor.irq(handler = OuterSensor_irq)

    else:
        OuterSensor = Pin(OuterSensorGPIOnum, Pin.IN, Pin.PULL_DOWN)
        OuterSensor.irq(handler=None)

def OuterSensor_irq():
    CheckDistance = True #may need callback function if sensors are not aligned

    

