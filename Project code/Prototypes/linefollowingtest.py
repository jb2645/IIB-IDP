#Main Code
from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
from utime import sleep

#definitions

#Defining Button
button_pin = 14         #to be determined
button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
running = True

#Defining Rover
motorL = Motor(dirPin=4, PWMPin=5)#check values later
motorR = Motor(dirPin=6, PWMPin=7)
sensors = Optocoupler(6, 7, 8, 9)
Robot = Rover(motorL, motorR, sensors) #update as more components added
follower = LineFollow(Robot, sensors)

if __name__ == "__main__":
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    bays = [1,2,6,7]
    pos = Position(grid)
    
    while running == False:
        pass

    while running == True:
        
        state = sensors.junction_detection()
        follower.update()
        if state!='CLEAR':
            #if state=='NODE':
            #    row = pos.find_row():
            #    if row in bays or row==0:
            #        pos.on_node()
            #    elif row==2:
            #        #turn to row 4
                
            if state=='TURN':
                left_value, right_value = sensors.read_junction()
                
                if left_value>right_value:
                    #turn left
                    Robot.turnleft()
                    pos.turn_end(1)
                    
                else:
                    pos.turn_end(0)
                    #turn right 
                    Robot.turnright()
        
        time.sleep(0.01)
        

        
        
            
            
            
            
            
            





#define button press interrupt to stop/start program
            
def button_pressed(pin):
    running = not running
    ##testing
    print("Button Pressed!")

button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)