#Main Code
from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
from utime import sleep

#definitions

#define button press interrupt to stop/start program
running = False         
def button_pressed(pin):
    global running
    running = not running
    ##testing
    print("Button ")

#Defining Button
button_pin = 22         #to be determined
button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)

#Defining Rover
motorL = Motor(dirPin=4, PWMPin=5)#check values later
motorR = Motor(dirPin=7, PWMPin=6)
sensors = Optocoupler(12, 21, 14, 20)
Robot = Rover(motorL, motorR, sensors) #update as more components added
follower = LineFollow(Robot, sensors)

if __name__ == "__main__":
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    bays = [1,2,6,7]
    pos = Position(grid)
    
    path = Path_LFT(Robot, sensors)
    
 #   follower = LineFollow(drive, sensors)
    while running == False:
        Robot.stop()
    while running == True:
        event = sensors.junction_detection()
        #pos.update(event) changed to path for line following test
        path.update()
        
        if pos.state == "CLEAR":
            follower.adjust()
            
        elif pos.state == "NODE":
            Robot.stop()
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
        

        