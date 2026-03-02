#Main Code
from "General Component Classes.py" import *
from "Linefollowing.py" import *
from "General Component Classes.py" import *
from machine import Pin
from utime import sleep

#definitions

#Defining Button
button_pin = 14         #to be determined
button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
running = False

#Defining Rover
motorL = Motor(dirPin=4, PWMPin=5)#check values later
motorR = Motor(dirPin=6, PWMPin=7)
Robot = Rover(motorL, motorR) #update as more components added

if __name__ == "__main__":
    while running == False:
        pass

    while running == True:
        if Robot.GetRoverState() == "Travel":
            #run line following program
        elif Robot.GetRoverState() == "Sensing":
            #run sensing routine

            
            
    ####Main code#####
    
    
    #write condition to switch off if running == false
            
            
            
            
            
            
            





#define button press interrupt to stop/start program
            
def button_pressed(pin):
    running = !running
    ##testing
    print("Button Pressed!")

button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)



    
    