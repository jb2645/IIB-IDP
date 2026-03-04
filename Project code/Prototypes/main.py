#Main Code
from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
import time
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
            
        elif running:
            running = False
            print("STOPPED")

    last_press_time = currenttime
    
#define button press interrupt to stop/start program

button_pin = 22
button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)

#Defining Rover
motorL = Motor(dirPin=4, PWMPin=5)#check values later
motorR = Motor(dirPin=7, PWMPin=6)
sensors = Optocoupler(12, 21, 14, 20)
Robot = Rover(motorL, motorR, sensors)
follower = LineFollow(Robot, sensors)

running = True
if __name__ == "__main__":
    while running == False:
        pass

    while running == True:
        #if Robot.GetRoverState() == "Travel":
            #run line following program
        #elif Robot.GetRoverState() == "Sensing":
            #run sensing routine

        Robot.drive(100, 100)
        print(1)
        time.sleep(1)
        running = False
    Robot.stop()
            
    ####Main code#####
    
    
    #write condition to switch off if running == false
            
            
            
            
            
            
            




    
    