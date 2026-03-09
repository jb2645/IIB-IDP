from machine import Pin, PWM
from utime import sleep
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
    def __init__(self, drive, sensors, base_speed=70, correction=25):
        self.drive = drive
        self.sensors = sensors
        self.base_speed = base_speed
        self.correction = correction
        
    def adjust(self):
        left, right = self.sensors.read_line()
        
        if left == 0 and right == 0:
            self.drive.drive(self.base_speed, self.base_speed)

        elif left == 0 and right == 1:
            self.drive.drive(self.base_speed - self.correction,
                             self.base_speed + self.correction)

        elif left == 1 and right == 0:
            self.drive.drive(self.base_speed + self.correction,
                             self.base_speed - self.correction)
        
        else:
            self.drive.drive(self.base_speed, self.base_speed)

    def reverseadjust(self):
        left, right = self.sensors.read_line()
        
        if left == 0 and right == 0:
            self.drive.drive(-self.base_speed, -self.base_speed)

        elif left == 0 and right == 1:
            self.drive.drive(-self.base_speed + self.correction,
                             -self.base_speed - self.correction)

        elif left == 1 and right == 0:
            self.drive.drive(-self.base_speed - self.correction,
                             -self.base_speed + self.correction)
        
        else:
            self.drive.drive(-self.base_speed, -self.base_speed)

class Position:
    def __init__(self, grid, end_nodes):
        self.grid = grid
        self.row = 0
        self.enode = end_nodes
        self.heading = 0  # [N, E, S, W] = [0, 1, 2, 3]
        self.node = 2     # Starting node
        self.state = "CLEAR"
        
    def update(self, event):
        self.state = event
        
    def find_row(self):
        if self.heading == 0 or self.heading == 1:
            return self.grid[self.row][0]
        else:
            return self.grid[self.row][1]
     
    def on_node(self):
        # FIRST: Increment node (we've arrived at a new junction)
        if self.heading == 0 or self.heading == 1:  # N or E → counting up
            self.node += 1
        else:  # S or W → counting down
            self.node -= 1
        
        print(f"Arrived at node {self.node}, row {self.row}")
        
        # THEN: Check if it's an end node
        end = self.enode[self.row]
        
        if self.node in end:
            print(f"END NODE - TURN!")
            return "TURN"
        else:
            return "NODE"
            
    def turn_end(self, turn):
        self.row = self.find_row()
        
        if turn == 0:  # right
            self.heading = (self.heading + 1) % 4
        elif turn == 1:  # left
            self.heading = (self.heading - 1) % 4
        
        # Reset node to starting position for new row
        new_end_row = self.enode[self.row]
            
        if self.heading == 0 or self.heading == 1:  # N or E
            self.node = new_end_row[1]  # Start from low end
        else:  # S or W
            self.node = new_end_row[0]  # Start from high end
            
        print(f"After turn: row={self.row}, heading={self.heading}, node={self.node}")
        
        
        
        
                

            


'''class Path_LFT:
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
        #print(self.state)
        old_state = self.state
        if self.state!=old_state:
            print(self.state)
        event = self.sensors.junction_detection()
        

        if self.state == "LEAVING_START":
            #print(self.junction)
            # Follow until first turn
            #print(event)
            if event == "JUNCTION" and self.junction==False:
                self.start_nodes+=1
                #print(self.start_nodes)
                if self.start_nodes == 2:
                    self.drive.drive_onto_junction()
                    self.drive.turnleft()
                    #self.pos.turn_end(1)
                    self.pos.heading = 3
                    self.state = "OUTER_LOOP"
            else:
                self.follower.adjust()

        elif self.state == "OUTER_LOOP":
            if event == "JUNCTION" and self.junction == False:
                sleep(0.1)
                nodestate = self.pos.on_node()
                print(nodestate)
                if nodestate == "TURN":
                    
                    self.turn_count += 1
                    self.drive.drive_onto_junction()
                    self.drive.turnright()
                    self.pos.turn_end(0)
                

                    if self.turn_count == 4:
                        self.state = "RETURNING"
                elif nodestate == "NODE":
                    self.drive.drive(45,45)
            else:
                self.follower.adjust()

        elif self.state == "PICKUP":
            #finished = False
            #blockdistance = 10
            #while blockdistance > 1:   #drives toward block until within 1cm - distance to be determined
            #    blockdistance = self.drive.getDistance("F")
            #    self.follower.adjust()
            #self.drive.stop()
            #self.drive.pickup()
            #colour = self.drive.DetermineColour()   
            #while
            #self.drive.reverseright() #sam to change with pathing algorithm
            #self.state = "RETURNING"

            ##Rewrite to fit style
            blockdistance  = self.drive.getDistance("F")
            if event == "JUNCTION":
                self.drive.reverseleft()   #sam to implement pathing later
                self.state = "RETURNING" # again pathing check later

            elif blockdistance < 1:
                self.drive.stop()
                self.drive.pickup()
                colour = self.drive.DetermineColour() 
                #self.drive.SetBlockStatus(True)

            elif self.drive.GetBlockStatus() == True:
                self.follower.reverseadjust()
            else: 
                self.follower.adjust()





        elif self.state == "RETURNING":
            if event == "JUNCTION" and self.junction == False:
                self.pos.on_node()
                if self.pos.node == 2:
                    self.drive.drive_onto_junction()
                    self.drive.turnleft()
                    self.state = "STOP"
            else:
                self.follower.adjust()

        elif self.state == "STOP":
            self.drive.drive(45,45)
            sleep(0.3)
            self.drive.stop()
            
        if event == "JUNCTION":
            self.junction = True
        elif event == "CLEAR":
            self.junction = False'''
        
        
class Path:
    def __init__(self, drive, sensors,pos, follower):
        self.drive = drive
        self.sensors = sensors
        self.pos = pos
        self.follower = follower
        
        #states
        self.state = "LEAVING_START"
        self.pos_state = "START"
        self.checked_nodes = set()
        
        #position counters
        self.turn_count = 0
        self.start_nodes = 0
        
        #junction error avoidance
        self.junction = False
        self.time_since_junction = 0
        self.junction_debounce = 300
        
        #saved position
        self.saved_position = None
        self.saved_state = None
        self.saved_pos_state = None
        self.saved_turn_count = 0
        
        #block and delivery targets
        self.block_colour = None
        self.delivery_target = None
        
    def save_position(self):
        #save current position for later return
        self.saved_position = {
            "row": self.pos.row,
            "node": self.pos.node,
            "heading": self.pos.heading
        }
        self.saved_state = self.state
        self.saved_pos_state = self.pos_state
        self.saved_turn_count = self.turn_count
        
    def restore_position(self):
        if self.saved_position:
            self.pos.row = self.saved_position["row"]
            self.pos.node = self.saved_position["node"]
            self.pos.heading = self.saved_position["heading"]
            self.state = self.saved_state
            self.pos_state = self.saved_pos_state
            self.turn_count = self.saved_turn_count
            
            self.saved_position = None
            
    def check_for_block(self):
        #whatever jack has come up with might not even need this function here
        #imagine a try except statement checking if block is present
        pass
    
    def at_block(self):
        #similarly whatever jack chooses
        #imagine try except statement that reads how far block is
        pass

        
    
    def find_route_to(self,target_row,target_node):
        current_row = self.pos.row
        current_node = self.pos.node
        current_heading = self.pos.heading
        
        route = []
        
        return route
        #this needs to be extended/changed
        #when called it returns info on where to go to return back to previous position
        #maybe all that is needed is a turn count
    
    def debounce_junction(self,event):
        if event!="JUNCTION":
            self.junction = False
            return False
        
        current_time = time.ticks(ms)
        
        if not self.junction:
            if time.ticks_diff(current_time, self.last_junction_time):
                self.junction = True
                self.last_junction_time = current_time
                return True
        return False
        
    def update(self):
        event = self.sensors.junction_detection()
        junction_triggered = self.debounce_junction(event)
        

        

        if self.state == "LEAVING_START":
            #print(self.junction)
            # Follow until first turn
            #print(event)
            if junction_triggered:
                self.start_nodes+=1
                #print(self.start_nodes)
                if self.start_nodes == 2:
                    self.drive.drive_onto_junction()
                    self.drive.turnleft()
                    #self.pos.turn_end(1)
                    self.pos.heading = 3
                    self.state = "SENSING"
                    self.pos_state = "OUTER_LOOP"
            else:
                self.follower.adjust()
                
        elif self.state == "SENSING":
            
            if self.pos.row in [1,2,6,7]:
                current = (self.pos.row,self.pos.node)
                if current not in self.checked_nodes:
                    self.drive.getDistance("F")
                    #sensing on
                    #now need to check if block is present and do something
                    self.checked_nodes.add(current)
                
            
            if self.pos_state == "OUTER_LOOP":
                if junction_triggered:
                    sleep(0.1)
                    nodestate = self.pos.on_node()
                    if nodestate == "TURN":
                    
                        self.turn_count += 1
                        self.drive.drive_onto_junction()
                        self.drive.turnright()
                        self.pos.turn_end(0)
                    

                        if self.turn_count == 4:
                            self.pos_state = "RAMP"
                            self.turn_count = 0
                    elif nodestate == "NODE":
                        self.drive.drive(45,45)
                else:
                    self.follower.adjust()
                    
            elif self.pos_state == "RAMP":
                if junction_triggered:
                    nodestate = self.pos.on_node()
                   
                   #gonna use if statements as phases for position
                    
                    #phase 1 - go to bottom of ramp
                    if self.turn_count < 2:
                        if nodestate == "TURN":
                            self.turn_count+=1
                            self.drive.drive_onto_junction
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            
                        elif nodestate = "NODE":
                            self.drive.drive(45,45)
                    
                    
                    #phase 2 - go onto ramp
                    elif self.turn_count == 2:
                        if nodestate == "NODE":
                            self.turn_count+=1
                            self.drive.drive_onto_junction
                            self.drive.turnright()
                            self.pos.turn_end(0)
                    
                    
                    #phase 3 - goto pickup bay        
                    elif self.turn_count < 5 and self.turn_count >2:
                        if nodestate == "TURN":
                            self.turn_count+=1
                            self.drive.drive_onto_junction
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            
                        elif nodestate = "NODE":
                            self.drive.drive(45,45)
                            
                    #phase 4 - reverse out of bay
                    #phase 5 - onto second bay
                    #phase 6 - reverse out of bay
                    #phase 7 - leave ramp and return home
                    

                    
                    
                else:
                    self.follower.adjust()
                
    

        elif self.state == "PICKUP":
            #finished = False
            #blockdistance = 10
            #while blockdistance > 1:   #drives toward block until within 1cm - distance to be determined
            #    blockdistance = self.drive.getDistance("F")
            #    self.follower.adjust()
            #self.drive.stop()
            #self.drive.pickup()
            #colour = self.drive.DetermineColour()   
            #while
            #self.drive.reverseright() #sam to change with pathing algorithm
            #self.state = "RETURNING"

            ##Rewrite to fit style
            blockdistance  = self.drive.getDistance("F")
            if event == "JUNCTION":
                self.drive.reverseleft()   #sam to implement pathing later
                self.state = "RETURNING" # again pathing check later

            elif blockdistance < 1:
                self.drive.stop()
                self.drive.pickup()
                colour = self.drive.DetermineColour() 
                #self.drive.SetBlockStatus(True)

            elif self.drive.GetBlockStatus() == True:
                self.follower.reverseadjust()
            else: 
                self.follower.adjust()





        elif self.state == "RETURNING":
            if event == "JUNCTION" and self.junction == False:
                self.pos.on_node()
                if self.pos.node == 2:
                    self.drive.drive_onto_junction()
                    self.drive.turnleft()
                    self.state = "STOP"
            else:
                self.follower.adjust()

        elif self.state == "STOP":
            self.drive.drive(45,45)
            sleep(0.3)
            self.drive.stop()
            
   





