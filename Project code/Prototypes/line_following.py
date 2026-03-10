from machine import Pin, PWM
from utime import sleep
import time

from general_component_classes import *
from rover_class_creation import * 
 
        

class LineFollow:
    def __init__(self, drive, sensors, base_speed=75, correction=20):
        self.drive = drive
        self.sensors = sensors
        self.base_speed = base_speed
        self.correction = correction
        
    def adjust(self):
        left, right = self.sensors.read_line()
        
        if left == 0 and right == 0:
            self.drive.drive(self.base_speed, self.base_speed)

        elif left == 0 and right == 1:
            self.drive.drive(self.base_speed + self.correction,
                             self.base_speed - self.correction)

        elif left == 1 and right == 0:
            self.drive.drive(self.base_speed - self.correction,
                             self.base_speed + self.correction)
        
        else:
            self.drive.drive(self.base_speed, self.base_speed)

    '''def reverseadjust(self):
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
'''
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
        
    def U_turn(self):
        self.heading = (self.heading+2)%4
        
        
class Path:
    def __init__(self, drive, sensors,pos, follower):
        self.drive = drive
        self.sensors = sensors
        self.pos = pos
        self.follower = follower
        self.distance = 0
        
        #states
        self.state = "LEAVING_START"
        self.pos_state = "START"
        self.checked_nodes = set()
        
        #position counters
        self.turn_count = 0
        self.start_nodes = 0
        self.dropoff_turn_count = 0
        
        #junction error avoidance
        self.junction = False
        self.last_junction_time = 0
        self.junction_debounce = 300
        
        #saved position
        self.current_row = 0
        self.saved_position = None
        self.saved_state = None
        self.saved_pos_state = None
        self.saved_turn_count = 0
        
        #block and delivery targets
        self.colour = None
        self.delivery_target = None

        #Flag for block check
        self.noblock = False
        
    def save_position(self):
        #save current position for later return
        self.saved_pos_state = self.pos_state
        
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
    
    def debounce_junction(self,event):
        if event!="JUNCTION":
            self.junction = False
            return False
        
        current_time = time.ticks_ms()
        
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
                print(self.start_nodes)
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
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            
                        elif nodestate == "NODE":
                            self.drive.drive(60,60)
                    
                    
                    #phase 2 - go onto ramp
                    elif self.turn_count == 2:
                        if nodestate == "NODE":
                            self.turn_count+=1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                        else:
                            self.drive.drive(60,60)
                    
                    
                    #phase 3 - goto pickup bay        
                    elif self.turn_count < 5 and self.turn_count >2:
                        if nodestate == "TURN":
                            self.turn_count+=1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            
                        elif nodestate == "NODE":
                            self.drive.drive(45,45)
                            
                    #phase 4 - leave bay
                    #U-turn then straight then left
                    elif self.turn_count <7 and self.turn_count>4:
                        if nodestate == "TURN" and self.turn_count == 5:
                            self.turn_count+=1
                            self.pos.U_Turn()
                            self.drive.LeftUTurn()
                            #do a left U-turn
                            self.pos.node+=-1
                        elif nodestate == "TURN" and self.turn_count == 6:
                            self.turn_count+=1
                            self.drive.drive_onto_junction()
                            self.drive.turn_left()
                            self.pos.turn_end(1)
                        else:
                            self.drive.drive(60,60)
                    
                            
                    #phase 5 - onto second bay
                    #straight to end then left
                    elif self.turn_count == 7:
                        if nodestate == "TURN":
                            self.turn_count+=1
                            self.drive.drive_onto_junction()
                            self.drive.turn_left()
                            self.pos.turn_end(1)
                        else:
                            self.drive.drive(60,60)
                    
                    #phase 6 - leave bay
                    #U-turn then straight then right
                    elif self.turn_count <10 and self.turn_count>7:
                        if nodestate == "TURN" and self.turn_count == 8:
                            self.turn_count+=1
                            self.pos.U_Turn()
                            self.drive.RightUTurn()
                            self.pos.node+=-1
                        elif nodestate == "TURN" and self.turn_count == 9:
                            self.turn_count+=1
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                        else:
                            self.drive.drive(60,60)
                    
                    #phase 7 - leave ramp and return home
                    #right, right, right, right, in
                    elif self.turn_count == 10:
                        self.turn_count+=1
                        self.drive.drive_onto_junction()
                        self.drive.turn_right()
                        self.pos.turn_end(0)
                        
                    elif self.turn_count>10 and self.turn_count<14:
                        if nodestate == "TURN":
                            self.turn_count+=1
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                        else:
                            self.drive.drive(60,60)
                    
                    elif self.turn_count == 14:
                        self.state = "BEDTIME"
                        

                    
                    
                else:
                    self.follower.adjust()
                   
            if self.pos.row in [1,3,6,7]:
                current = (self.pos.row,self.pos.node)
                if current not in self.checked_nodes:
                    self.distance = self.drive.getDistance("R")
                    print(self.distance)
                    if self.distance < 270:
                        self.state = "PICKUP"
                        self.drive.turnright()     #should probably fix properly later
                        self.save_position()
                    #sensing on
                    #now need to check if block is present and do something
                    self.checked_nodes.add(current)
            

        elif self.state == "PICKUP":


            ##Rewrite to fit style
            #blockdistance  = self.drive.getDistance("F")
            blockdistance = 301
            '''if event == "JUNCTION":
                self.drive.reverseleft()   #sam to implement pathing later
                self.state = "RETURNING"''' # again pathing check later

            if blockdistance > 300 and self.drive.GetBlockStatus() == False:
                self.noblock = True
                self.drive.RightUTurn()

            if blockdistance < 10:
                self.drive.stop()
                self.drive.pickup()
                colour = self.drive.DetermineColour() 
                #self.drive.SetBlockStatus(True)

            elif self.drive.GetBlockStatus() == True:
                self.drive.RightUTurn()
                
            elif junction_triggered:
                if self.noblock == True:
                    if self.pos.row in [1, 7]:   #again sam check pathing
                        self.drive.turnright()
                    else:
                        self.drive.turnleft()
                    self.state = "SENSING"
                else:
                    self.state = "DROPOFF"
                    self.current_row = self.pos.row
                    self.colour = self.drive.DetermineColour()

            else: 
                self.follower.adjust()
                
        elif self.state == "PUTDOWN":
            if event == "JUNCTION":
                self.drive.drive(70,70)
                sleep(0.3)
                self.drive.putdown()
                self.LeftUTurn()
                self.pos.U_Turn()
                self.drive.drive(70,70)
                sleep(0.5)
                self.state = "RETURNING"
            else:
                self.adjust()
                    
                    
        elif self.state == "DROPOFF":
            if self.current_row == 1:
                if self.dropoff_turn_count == 0:
                    self.drive.turn_left()
                    self.pos.U_Turn
                    self.dropoff_turn_count +=1
                    
                else:
                    if junction_triggered:
                        nodestate = self.pos.on_node
                        if nodestate == "TURN" and self.colour == "Blue":
                            self.state = "PUTDOWN"
                            self.dropoff_turn_count =0
                            
                        elif nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turn_left()
                            self.pos.turn_end(1)
                            self.dropoff_turn_count+=1
                        
                        elif self.dropoff_turn_count == 2:
                            if self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                                
                            elif self.pos.node == 4 and self.colour == "Red":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                
                    else:
                        self.follower.adjust()
                
                    
            elif self.current_row == 3:
                if self.dropoff_turn_count == 0:
                    self.drive.turn_right()
                    self.dropoff_turn_count +=1
                    
                else:
                    if junction_triggered:
                        nodestate = self.pos.on_node
                        if nodestate == "TURN" and self.colour == "Red":
                            self.state = "PUTDOWN"
                            self.dropoff_turn_count =0
                            
                        elif nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count+=1
                        elif self.dropoff_turn_count == 2:
                            if self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turn_left()
                                self.pos.turn_end(1)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turn_left()
                                self.pos.turn_end(1)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                                
                            elif self.pos.node == 4 and self.colour == "Red":
                                self.drive.drive_onto_junction()
                                self.drive.turn_left()
                                self.pos.turn_end(1)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                    else:
                        self.follower.adjust()
                
                    
            elif self.current_row == 6:
                if self.dropoff_turn_count == 0:
                    self.drive.turn_right()
                    self.pos.U_Turn
                    self.dropoff_turn_count +=1
                    
                else:
                    if junction_triggered:
                        nodestate = self.pos.on_node
                            
                        if nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turn_left()
                            self.pos.turn_end(1)
                            self.dropoff_turn_count+=1
                        
                        elif nodestate == "NODE" and self.dropoff_turn_count ==2:
                            self.drive.drive_onto_junction()
                            self.drive.turn_left()
                            self.pos.turn_end(1)
                            self.dropoff_turn_count+=1
                        
                        elif nodestate == "TURN" and self.dropoff_turn_count < 4:
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count+=1
                            
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4 and self.colour== "Red":
                            self.state == "PUTDOWN"
                            self.dropoff_turn_count == 0
                            
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4:
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count+=1
                            
                        
                        elif self.dropoff_turn_count == 5:
                            if self.pos.node == 0 and self.colour == "Blue":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                            elif self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                
                    else:
                        self.follower.adjust()
                    
            elif self.current_row == 7:
                if self.dropoff_turn_count == 0:
                    self.drive.turn_left()
                    self.pos.U_Turn
                    self.dropoff_turn_count +=1
                    
                else:
                    if junction_triggered:
                        nodestate = self.pos.on_node
                            
                        if nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count+=1
                        
                        elif nodestate == "NODE" and self.dropoff_turn_count ==2:
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count+=1
                        
                        elif nodestate == "TURN" and self.dropoff_turn_count < 4:
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count+=1
                            
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4 and self.colour== "Red":
                            self.state == "PUTDOWN"
                            self.dropoff_turn_count == 0
                            
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4:
                            self.drive.drive_onto_junction()
                            self.drive.turn_right()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count+=1
                            
                        
                        elif self.dropoff_turn_count == 5:
                            if self.pos.node == 0 and self.colour == "Blue":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                            elif self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turn_right()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count=0
                
                    else:
                        self.follower.adjust()
            

                
        elif self.state == "RETURNING":
            if self.colour == "Blue":
                self.drive.drive(60,60)
                sleep(0.3)
                self.turn_count = 1
                self.pos.node = 0
            else:
                self.drive.turn_left()
                self.pos.turn_end(1)
                self.turn_count = 0
            self.state = "SENSING"

        elif self.state == "BEDTIME":
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
            
   





