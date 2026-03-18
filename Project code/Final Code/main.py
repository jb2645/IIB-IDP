#importing libraries
from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
import machine
import time
from utime import sleep


#setting up global variables
running = False
reboot_flag = False  # ← New flag
last_press_time = 0
DEBOUNCE_MS = 200
DOUBLE_PRESS_MS = 500

# Defining Button and interrupt
def button_pressed(pin):            #Function run to start/stop program when button is pressed
    global running, last_press_time, reboot_flag

    currenttime = time.ticks_ms()
    time_since_last = time.ticks_diff(currenttime, last_press_time)

    if time_since_last > DEBOUNCE_MS:       #debrounce timer to ensure button is not double pressed
        running = not running
        
        if running:
            pass
           # print("STARTED")
        else:
            Robot.stop()                
            Robot.stowGrabber()
           # print("STOPPED")

    last_press_time = currenttime

button_pin = 22
button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)
    

# Main Code
if __name__ == "__main__":
    while True:
        motorR = Motor(dirPin=4, PWMPin=5)
        motorL = Motor(dirPin=7, PWMPin=6)
        sensors = Optocoupler(12, 21, 14, 20)
        verticalservo = Servo(15)
        horizontalservo = Servo(13)
        Robot = Rover(motorL, motorR, sensors, horizontalservo, verticalservo)
        follower = LineFollow(Robot, sensors)

        #defining map of the course
        grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
        end_nodes = [(4,0),(8,0),(2,0),(8,0),(1,0),(2,0),(7,0),(7,0)]
        bays = [1,2,6,7]
        pos = Position(grid, end_nodes)
        
        path = Path(Robot, sensors, pos, follower)
        
        # Main outer loop
        while running:
            
            # Check for reboot request
            if reboot_flag:
                print("REBOOTING...")
                Robot.stop()
                sleep(0.1)
                #machine.soft_reset()
            
            # Wait until button pressed
            if not running:
                Robot.stop()
                sleep(0.01)
                continue  # ← Go back to top of loop
            
            # Running - do path update
            path.update()
            sleep(0.06)

        sleep(0.1)





