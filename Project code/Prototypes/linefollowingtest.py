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
sensors = Optocoupler(12, 21, 14, 20)
Robot = Rover(motorL, motorR, sensors) #update as more components added
follower = LineFollow(Robot, sensors)

if __name__ == "__main__":
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    bays = [1,2,6,7]
    pos = Position(grid)
    
    path = Path_LFT(drive, sensors)
    
 #   follower = LineFollow(drive, sensors)
    
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
     #               drive.turnleft()
                    pos.turn_end(1)
                    
                else:
                    pos.turn_end(0)
                    #drive.turnright()
                    #turn right 

        time.sleep(0.01)
        

        
        
            
            
            
            
            
            





#define button press interrupt to stop/start program
            
def button_pressed(pin):
    running = not running
    ##testing
    print("Button Pressed!")

button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)