from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
import time
from utime import sleep


running = False
reboot_flag = False  # ← New flag
last_press_time = 0
DEBOUNCE_MS = 200
DOUBLE_PRESS_MS = 500

def button_pressed(pin):
    global running, last_press_time, reboot_flag

    currenttime = time.ticks_ms()
    time_since_last = time.ticks_diff(currenttime, last_press_time)

    if time_since_last > DEBOUNCE_MS:
        
        # Check for double press
        if time_since_last < DOUBLE_PRESS_MS:
            reboot_flag = True  # ← Set flag instead of resetting here
        
        else:
            # Single press - toggle start/stop
            running = not running
            
            if running:
                print("STARTED")
            else:
                Robot.stop()
                print("STOPPED")

    last_press_time = currenttime


# Defining Button
button_pin = 22
button = Pin(button_pin, Pin.IN, Pin.PULL_DOWN)
button.irq(trigger=Pin.IRQ_RISING, handler=button_pressed)

#Defining Rover
motorL = Motor(dirPin=4, PWMPin=5)#check values later
motorR = Motor(dirPin=7, PWMPin=6)
sensors = Optocoupler(12, 21, 14, 20)
verticalservo = Servo(15)
horizontalservo = Servo(13)
Robot = Rover(motorL, motorR, sensors, horizontalservo, verticalservo)
follower = LineFollow(Robot, sensors)

\

if __name__ == "__main__":        
    # Wait until button pressed
    while not running:
        Robot.stop()
        time.sleep(0.01)

    # Main loop
    while running:

        #Robot.stowGrabber()
        #Robot.test()
        #sleep(1)
        #print(Robot.DetermineColour())
        #sleep(1)
        #Robot.stowGrabber()
        #sleep(1)
       # Robot.release()
        Robot.pickup()
        Robot.DetermineColour()
        
        sleep(5)
       # Robot.stowGrabber()
        
        
        #print(Robot.DetermineColour())
        #print(Robot.getDistance("F"), Robot.getDistance("R"))
        #Robot.putdown()
        