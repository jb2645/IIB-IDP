from machine import Pin, PWM
from utime import sleep

from general_component_classes import *
from rover_class_creation import * 
import time


DEBUG = False
def debug_print(*args):
    if DEBUG:
        print(*args)

class LineFollow: #Handles line following with the inner sensors
    def __init__(self, drive, sensors, base_speed=80, correction=20):

        self.drive = drive
        self.sensors = sensors
        self.base_speed = base_speed
        self.correction = correction



        
        self.speed_left_correct = max(0,min(100,base_speed + correction))
        self.speed_right_correct = max(0,min(100,base_speed - correction))
        
    def setbasespeed(self,speed):
        self.base_speed = speed
    
    def adjust(self):
        left, right = self.sensors.read_line()
        
        if left == 0 and right == 0:
            # Both sensors on line - drive straight
            self.drive.drive(self.base_speed, self.base_speed)

        elif left == 0 and right == 1:
            # Drifting right - correct left
            self.drive.drive(self.speed_left_correct,
                             self.speed_right_correct)

        elif left == 1 and right == 0:
            # Drifting left - correct right
            self.drive.drive(self.speed_right_correct,
                             self.speed_left_correct)
        
        else:
            # Both off line - drive straight (recovery)
            self.drive.drive(self.base_speed, self.base_speed)



class Position: #Tracks rover's position on grid
    def __init__(self, grid, end_nodes):
        self.grid = grid
        self.row = 0
        self.enode = end_nodes
        self.heading = 0      # [N, E, S, W] = [0, 1, 2, 3]
        self.node = 2         # Starting node
        self.state = "CLEAR"
        
    def update(self, event):
        self.state = event
        
    def find_row(self):#Determines what row rover is on following turn
        if self.heading <2:
            return self.grid[self.row][0]
        else:
            return self.grid[self.row][1]
     
    def on_node(self):#updates node count then checks if its a turn
        if self.heading <2:  # N or E → counting up
            self.node += 1
        else:  # S or W → counting down
            self.node -= 1
        
        debug_print(f"Arrived at node {self.node}, row {self.row}")
        
        # Check if it's an end node (need to turn)
        end = self.enode[self.row]
        
        if self.node in end:
            debug_print(f"END NODE - TURN!")
            return "TURN"
        else:
            return "NODE"
            
    def turn_end(self, turn):
        # Update row
        self.row = self.find_row()
        
        # Update heading
        if turn == 0:  # right
            self.heading = (self.heading + 1) & 3
        elif turn == 1:  # left
            self.heading = (self.heading - 1) & 3
        
        # Reset node to starting position for new row
        new_end_row = self.enode[self.row]
            
        if self.heading <2:  # N or E
            self.node = new_end_row[1]  # Start from low end
        else:  # S or W
            self.node = new_end_row[0]  # Start from high end
            
        debug_print(f"After turn: row={self.row}, heading={self.heading}, node={self.node}")
        
    def U_turn(self):
        """Reverse heading direction (180 degree turn)"""
        self.heading = (self.heading + 2) & 3


class Path: #Main state machine controlling behaviour
    def __init__(self, drive, sensors, pos, follower):
        self.drive = drive
        self.sensors = sensors
        self.pos = pos
        self.follower = follower
        self.distance = 0

        self.state = "LEAVING_START"    # Main state machine state
        self.pos_state = "START"        # Position state 
        self.checked_nodes = set()      # Nodes already checked for blocks

        self.checked_nodes.add((1, 0))

        self.turn_count = 0             # Turns made in current phase
        self.start_nodes = 0            # Nodes passed leaving start
        self.dropoff_turn_count = 0     # Turns made during dropoff navigation
        
        self.junction = False
        
        self.current_row = 0
        self.saved_pos_state = None
        
        self.noblock = False
        self.colour = None              # Detected block colour

        self.timer = 0 #dummy, remove after first test
        self.timerflag = False

        self.escaped = False
        
    def save_position(self):
        """Save current pos_state for returning after delivery"""
        self.saved_pos_state = self.pos_state
    


    def SetState(self, state):
        self.pos_state = state
    
    
    def update(self):
        """
        Main state machine update - call this in main loop
        
        States:
            LEAVING_START   → Navigate from start to main loop
            SENSING         → Follow route, check for blocks
            PICKUP          → Approach and pickup block
            DROPOFF         → Navigate to correct bay
            PUTDOWN         → Place block in bay
            RETURNING       → Return to route after delivery
            BEDTIME         → Return to start position
            STOP            → Final stop
        """
        
        event = self.sensors.junction_detection()
        is_new_junction = (event == "JUNCTION") and (not self.junction)
        


        if self.state == "LEAVING_START": #leaves starting area
            if is_new_junction:
                debug_print(self.start_nodes)
                self.start_nodes += 1
                
                if self.start_nodes == 2:
                    # At second node - turn left onto outer loop
                    self.drive.drive_onto_junction()
                    self.drive.turnleft()
                    self.pos.heading = 3    # Now heading West
                    self.state = "SENSING"
                    self.pos_state = "OUTER_LOOP"
                    self.drive.stowGrabber()
                    self.drive.grab()
            else:
                self.follower.adjust()

        elif self.state == "SENSING": #main path 
            
            if self.pos_state == "OUTER_LOOP": #outer perimeter
                if is_new_junction:
                    sleep(0.1)
                    nodestate = self.pos.on_node()
                    
                    if nodestate == "TURN":
                        # At corner - turn right
                        self.turn_count += 1
                        self.drive.drive_onto_junction()
                        self.drive.turnright()
                        self.pos.turn_end(0)

                        if self.turn_count == 4:
                            # Completed outer loop - move to ramp
                            self.pos_state = "RAMP"
                            self.turn_count = 0
                            
                    elif nodestate == "NODE":
                        # At intermediate node - drive through
                        self.drive.drive(60,60)
                else:
                    self.follower.adjust()
            

            elif self.pos_state == "RAMP": #navigates ramp and upper bays
                if is_new_junction:
                    sleep(0.1)
                    nodestate = self.pos.on_node()
                    tc = self.turn_count
                   
                    # Phase 1: Go to bottom of ramp (turns 0-1)
                    if tc < 2:
                        if nodestate == "TURN":
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)

                        elif nodestate == "NODE":
                            self.drive.drive(60, 60)
                    
                    # Phase 2: Turn onto ramp (turn 2)
                    elif tc == 2:
                        if nodestate == "NODE" and self.pos.node == 1:
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            #self.pos.turn_end(0)
                            self.pos.row = 4
                            self.pos.heading = 2
                            self.pos.node = 1
                            debug_print(f"After turn: row={self.pos.row}, heading={self.pos.heading}, node={self.pos.node}")
                        else:
                            self.drive.drive(60, 60)
                    
                    elif tc == 3:
                         if nodestate == "TURN":
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            #self.pos.turn_end(0)
                            self.pos.row = 5
                            self.pos.heading = 3
                            self.pos.node = 1
                            debug_print(f"After turn: row={self.pos.row}, heading={self.pos.heading}, node={self.pos.node}")
                         else:
                            self.drive.drive(60, 60)
                    
                    # Phase 3: Go to first pickup bay (turns 3-4)
                    elif tc == 4:
                        if nodestate == "TURN":
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                        elif nodestate == "NODE":
                            self.drive.drive(45, 45)
                            
                    # Phase 4: Leave first bay - U-turn then left (turns 5-6)
                    
                    elif tc == 5:
                        if nodestate == "TURN":
                            # U-turn at end of bay
                            self.turn_count += 1
                            self.pos.U_turn()
                            self.drive.LeftUTurn()
                            sleep(0.1)
                            self.pos.node = 6
                        else:
                            self.drive.drive(60,60)
                    elif tc == 6:
                        if nodestate == "TURN":
                            # Turn left to exit
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnleft()
                            self.pos.turn_end(1)
                        else:
                            self.drive.drive(60, 60)
                            
                    # Phase 5: Go to second bay - straight then left (turn 7)
                    elif tc == 7:
                        if nodestate == "TURN":
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnleft()
                            self.pos.turn_end(1)
                        else:
                            self.drive.drive(60, 60)
                    
                    # Phase 6: Leave second bay - U-turn then right (turns 8-9)
                    elif tc == 8:
                        if nodestate == "TURN":
                            # U-turn at end of bay
                            self.turn_count += 1
                            self.pos.U_turn()
                            self.drive.RightUTurn()
                            sleep(0.1)
                            self.pos.node = 6 
                        else:
                            self.drive.drive(60,60)
                            
                    elif tc == 9:
                        if nodestate == "TURN":
                            # Turn right to exit
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                        else:
                            self.drive.drive(60, 60)
                    
                    # Phase 7: Leave ramp and return home (turns 10-13)
                    elif tc == 10:
                        if nodestate == "NODE" or nodestate == "TURN":
                            # First turn off ramp
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                        
                    elif tc == 11:
                        self.pos.row = 4
                        self.pos.heading = 0
                        self.pos.node = 0
                        if nodestate == "TURN":
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                        else:
                            self.drive.drive(60,60)
                            
                    
                    elif tc < 14:
                        if nodestate == "TURN":
                            self.turn_count += 1
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                        else:
                            self.drive.drive(60, 60)
                    
                    # Phase 8: Route complete - go to bed
                    elif tc == 14:
                        self.state = "BEDTIME"
                else:
                    self.follower.adjust()

        
            
            
            if self.pos.row in [1, 3, 6, 7]: #block detection checks
                current = (self.pos.row, self.pos.node)
                #[[1, 0], []]
                if current not in self.checked_nodes:
                    # Check for block using right-side distance sensor
                    self.distance = self.drive.getDistance("R")
                    print(self.distance)
                    
                    if self.distance < 249:
                        # Block detected - switch to pickup mode
                        self.state = "PICKUP"
                        self.drive.drive_onto_junction()
                        self.drive.turnright()
                        self.save_position()
                    
                    # Mark this node as checked
                    self.checked_nodes.add(current)


        elif self.state == "PICKUP":
            blockdistance = self.drive.getDistance("F")
            
            if blockdistance > 300 and self.drive.GetBlockStatus() == False and self.noblock == False:
                # No block found - turn around
                self.noblock = True
                if self.noblock == True:
                    # No block was found - return to route
                    self.drive.drive_onto_junction()
                    if self.pos.row in [1, 7]:
                        self.drive.reverseright()
                    else:
                        self.drive.reverseleft()
                    self.state = "SENSING"
                    self.noblock = False
                debug_print(1)
            
            
            if blockdistance < 38 and self.drive.GetBlockStatus() == False:
                # Close enough to pickup, grabs block and turns around
                self.drive.stop()
                self.drive.pickup()
                self.drive.drive(-60, -60)
                sleep(0.2)
                self.drive.stowGrabber()
                sleep(0.2)
                self.drive.RightUTurn()
                self.drive.drive(-60, -60)
                sleep(0.2)

                         
            elif is_new_junction:
                sleep(0.1)
                # Block picked up - go to dropoff
                self.follower.setbasespeed(80)
                self.state = "DROPOFF"
                self.current_row = self.pos.row
                self.colour = self.drive.DetermineColour()
                
                self.noblock = True
            
            else:
                self.follower.setbasespeed(60)
                self.follower.adjust()
                debug_print(3)

                
        
        elif self.state == "PUTDOWN": #place block
            if is_new_junction and self.escaped == False:
                sleep(0.1)
                # Drive forward slightly then put down block
                self.drive.drive(70, 70)
                sleep(0.3)
                self.drive.putdown()
                
                # U-turn to exit bay
                self.drive.LeftUTurn()
                self.pos.U_turn()
                
                # Drive forward to clear bay
                self.drive.drive(70, 70)
                #sleep(0.5)
                self.escaped = True
                
            
            elif event == "JUNCTION":
                self.state = "RETURNING"
                self.escaped = False
            else:
                self.follower.adjust()
        
        elif self.state == "DROPOFF": #navigates to dropoff bays from various positions
            cr = self.current_row
            if cr == 1: 
                if self.dropoff_turn_count == 0:
                    # Initial turn to leave pickup area
                    self.drive.blockturnleft()
                    self.pos.U_turn()
                    self.dropoff_turn_count += 1
                else:
                    if is_new_junction:
                        sleep(0.1)
                        nodestate = self.pos.on_node()
                        
                        # Blue bay - first turn
                        if nodestate == "TURN" and self.colour == "Blue":
                            self.state = "PUTDOWN"
                            self.dropoff_turn_count = 0
                            
                        # First junction - turn left
                        elif nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turnleft()
                            self.pos.turn_end(1)
                            self.dropoff_turn_count += 1
                        
                        # Second phase - find correct bay
                        elif self.dropoff_turn_count == 2:
                            if self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                                
                            elif self.pos.node == 4 and self.colour == "Red":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                    else:
                        self.follower.adjust()
            
            elif cr == 3:
                if self.dropoff_turn_count == 0:
                    self.drive.blockturnright()
                    self.dropoff_turn_count += 1
                else:
                    if is_new_junction:
                        sleep(0.1)
                        nodestate = self.pos.on_node()
                        
                        # Red bay - first turn
                        if nodestate == "TURN" and self.colour == "Red":
                            self.state = "PUTDOWN"
                            self.dropoff_turn_count = 0
                            
                        # First junction - turn right
                        elif nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count += 1
                            
                        # Second phase - find correct bay
                        elif self.dropoff_turn_count == 2:
                            if self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turnleft()
                                self.pos.turn_end(1)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turnleft()
                                self.pos.turn_end(1)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                                
                            elif self.pos.node == 4 and self.colour == "Blue":
                                self.drive.drive_onto_junction()
                                self.drive.turnleft()
                                self.pos.turn_end(1)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                    else:
                        self.follower.adjust()
            
            elif cr == 6:
                if self.dropoff_turn_count == 0:
                    self.drive.blockturnright()
                    self.pos.U_turn()
                    self.dropoff_turn_count += 1
                else:
                    if is_new_junction:
                        sleep(0.1)
                        nodestate = self.pos.on_node()
                        
                        # First turn - go left
                        if nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turnleft()
                            self.pos.turn_end(1)
                            self.dropoff_turn_count += 1
                        
                        # Second junction (node) - turn left
                        elif nodestate == "NODE" and self.dropoff_turn_count == 2:
                            self.drive.drive_onto_junction()
                            self.drive.turnleft()
                            self.pos.turn_end(1)
                            self.dropoff_turn_count += 1
                        
                        # Continue turning right until phase 4
                        elif nodestate == "TURN" and self.dropoff_turn_count < 4:
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count += 1
                            
                        # Red bay at phase 4
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4 and self.colour == "Red":
                            self.state = "PUTDOWN"
                            self.dropoff_turn_count = 0
                            
                        # Continue if not red
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4:
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count += 1
                        
                        # Phase 5 - find correct bay by node position
                        elif self.dropoff_turn_count == 5:
                            if self.pos.node == 0 and self.colour == "Blue":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                                
                            elif self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                    else:
                        self.follower.adjust()
            
            
            elif cr == 7:
                if self.dropoff_turn_count == 0:
                    self.drive.blockturnleft()
                    self.pos.U_turn()
                    self.dropoff_turn_count += 1
                else:
                    if is_new_junction:
                        sleep(0.1)
                        nodestate = self.pos.on_node()
                        
                        # First turn - go right
                        if nodestate == "TURN" and self.dropoff_turn_count == 1:
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count += 1
                        
                        # Second junction (node) - turn right
                        elif nodestate == "NODE" and self.dropoff_turn_count == 2:
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count += 1
                        
                        # Continue turning right until phase 4
                        elif nodestate == "TURN" and self.dropoff_turn_count < 4:
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count += 1
                            
                        # Red bay at phase 4
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4 and self.colour == "Red":
                            self.state = "PUTDOWN"
                            self.dropoff_turn_count = 0
                            
                        # Continue if not red
                        elif nodestate == "TURN" and self.dropoff_turn_count == 4:
                            self.drive.drive_onto_junction()
                            self.drive.turnright()
                            self.pos.turn_end(0)
                            self.dropoff_turn_count += 1
                        
                        # Phase 5 - find correct bay by node position
                        elif self.dropoff_turn_count == 5:
                            if self.pos.node == 0 and self.colour == "Blue":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                                
                            elif self.pos.node == 1 and self.colour == "Green":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                            
                            elif self.pos.node == 3 and self.colour == "Yellow":
                                self.drive.drive_onto_junction()
                                self.drive.turnright()
                                self.pos.turn_end(0)
                                self.state = "PUTDOWN"
                                self.dropoff_turn_count = 0
                    else:
                        self.follower.adjust()


        elif self.state == "RETURNING": #returns to route following block delivery
            if self.colour == "Blue":
                # Blue bay special case - drive forward and set position
                self.drive.drive(60, 60)
                sleep(0.3)
                self.turn_count = 1
                self.pos.node = 0
            else:
                # Other bays - turn left and reset
                self.drive.turnleft()
                self.pos.turn_end(1)
                self.turn_count = 0
            
            # Return to sensing state (pos_state unchanged)
            self.state = "SENSING"


        elif self.state == "BEDTIME": #returns to starting position following completion
            if is_new_junction:
                sleep(0.1)
                self.pos.on_node()
                if self.pos.node == 2:
                    # At home position - turn in
                    self.drive.drive_onto_junction()
                    self.drive.turnleft()
                    self.state = "STOP"
            else:
                self.follower.adjust()

        elif self.state == "STOP": #turns off
            self.drive.drive(45, 45)
            sleep(0.3)
            self.drive.stop()
            debug_print("FINISHED")
            
        self.junction = (event == "JUNCTION")
