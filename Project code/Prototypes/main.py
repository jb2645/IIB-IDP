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

last_press_time = 0
DEBOUNCE_MS = 200   # debounce delay in milliseconds

def button_pressed():
    global running, last_press_time

    currenttime = time.ticks_ms()

    # Debounce check
    if time.ticks_diff(now, last_press_time) > DEBOUNCE_MS:
        if not running:      # Only allow start once
            running = True
            print("STARTED")
            
        if running:
            running = False
            print("STOPPED")

    last_press_time = currenttime
    
#define button press interrupt to stop/start program

button_pin = 22
button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)

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
            
            
            
            
            
            
            




    
    