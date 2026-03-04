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
'''
class LineSensors:
    def __init__(self,fleft_pin,left_pin,right_pin,fright_pin):
        self.fleft = Pin(fleft_pin,Pin.IN)
        self.left = Pin(left_pin,Pin.IN)
        self.right = Pin(right_pin,Pin.IN)
        self.fright = Pin(fright_pin,Pin.IN)
        
    
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
'''                
            
        

class LineFollow:
    def __init__(self, drive, sensors, base_speed=60, correction=20):
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
    def __init__(self,grid,end_nodes):
        self.grid = grid #((3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(x,5),(x,5))
        self.row = 0
        self.enode = end_nodes
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
     
    def on_node(self):
        end = self.enode[self.row]
        if self.node not in end:
            if self.heading == 0 or self.heading==1: # 0=North 1=east
                self.node+=1
            
            elif self.heading==3 or self.heading ==2: # 3=west  2=South
                self.node-=1
            return "NODE"
        
        elif self.node in end:
            if self.heading == 0 or self.heading==1: # 0=North 1=east
                self.node+=1
            
            elif self.heading==3 or self.heading ==2: # 3=west  2=South
                self.node-=1
            return "TURN"
        

            
            
    def turn_end(self,turn):
        old_row = self.row
        self.row = self.find_row()
        
        if turn == 0: #right
            self.heading = (self.heading+1)%4
            
            
        elif turn == 1: #left
            self.heading = (self.heading-1)%4
        
        new_end_row = self.enode[self.row]
            
        if self.heading == 0 or self.heading == 1:
            self.node = new_end_row[1]
            
        elif self.heading == 2 or self.heading == 3:
            self.node = new_end_row[0]
            
            
    def turn_node(self):
        if self.node == 6:
            pass
    

class Path_LFT:
    def __init__(self, drive, sensors,pos, follower):
        self.drive = drive
        self.sensors = sensors
        self.pos = pos
        self.follower = follower
        self.state = "LEAVING_START"
        self.turn_count = 0
        self.start_nodes = 0
        self.junction = False

    def update(self):
        print(self.state)

        event = self.sensors.junction_detection()
        if event == "JUNCTION":
            self.junction = True
        elif event == "CLEAR":
            self.junction = False
        

        if self.state == "LEAVING_START":
            # Follow until first turn
            if event == "JUNCTION" and self.junction==False:
                self.start_nodes+=1
                
                if self.start_nodes == 2:
                    self.drive.turnleft()
                    self.pos.turn_end(1)
                    self.state = "OUTER_LOOP"
            else:
                self.follower.adjust()

        elif self.state == "OUTER_LOOP":
            if event == "JUNCTION" and self.junction == False:
                nodestate = self.pos.on_node()
                if nodestate == "TURN":
                    
                    self.turn_count += 1
                    self.drive.turnright()
                    self.pos.turn_end(0)
                

                    if self.turn_count == 4:
                        self.state = "RETURNING"
            else:
                self.follower.adjust()

        elif self.state == "RETURNING":
            if event == "JUNCTION" and self.junction == False:
                self.pos.on_node()
                if self.pos.node == 2:
                    self.drive.turnleft()
                    self.state = "STOP"
            else:
                self.follower.adjust()

        elif self.state == "STOP":
            self.drive.stop()

'''
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
'''
    

