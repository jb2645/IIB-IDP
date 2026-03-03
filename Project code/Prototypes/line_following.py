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
    def __init__(self, drive, sensors, base_speed=40, correction=20):
        self.drive = drive
        self.sensors = sensors
        self.base_speed = base_speed
        self.correction = correction
        
    def adjust(self):
        left, right = self.sensor.read_line()
        
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
    

<<<<<<< Updated upstream
class Path_LFT:
    def __init__(self, drive, sensors):
        self.drive = drive
        self.sensors = sensors

        self.state = "LEAVING_START"
        self.turn_count = 0

    def update(self):

        event = self.sensors.get_event()

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




'''def main():
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    bays = [1,2,6,7]
    pos = Position(grid)
=======
def main():
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    bays = [1,2,6,7]
    pos = Position(grid)##
>>>>>>> Stashed changes

    
    left_motor = Motor(dirPin=4, PWMPin=5)#check values later
    right_motor = Motor(dirPin=6, PWMPin=7)

    #sensors = LineSensors(['''pin1,pin2,pin3,pin4'''])
    sensors = Optocoupler(6, 7, 8, 9)      #check actual order of gpio pins
    
    drive = MainDrive(left_motor, right_motor)
    drive = Rover(left_motor, right_motor, sensors) # This will need to be updated later when rover class completed
    
    path = Path_LFT(drive, sensors)
    
    follower = LineFollow(drive, sensors)
    
    while True:
        event = sensors.get_event()
        #pos.update(event) changed to path for line following test
        path.update()
        
        if pos.state == "CLEAR":
            follower.adjust()
            
        elif pos.state == "NODE":
            drive.stop()
            pos.on_node()
        
        elif pos.state == "TURN":
            left_value, right_value = sensors.read_junction()
                
                if left_value>right_value:
                    #turn left
                    drive.turnleft()
                    pos.turn_end(1)
                    
                else:
                    pos.turn_end(0)
                    drive.turnright()
                    #turn right 

        time.sleep(0.01)
        
#main()

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

    

