# Main Code
from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
import machine
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

motorL = Motor(dirPin=4, PWMPin=5)
motorR = Motor(dirPin=7, PWMPin=6)
sensors = Optocoupler(12, 21, 14, 20)
Robot = Rover(motorL, motorR, sensors)
follower = LineFollow(Robot, sensors)


if __name__ == "__main__":
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    end_nodes = [(4,0),(8,0),(2,0),(8,0),(1,0),(2,0),(7,0),(7,0)]
    bays = [1,2,6,7]
    pos = Position(grid, end_nodes)
    
    path = Path_LFT(Robot, sensors, pos, follower)
    
    # Main outer loop
    while True:
        
        # Check for reboot request
        if reboot_flag:
            print("REBOOTING...")
            Robot.stop()
            sleep(0.1)
            machine.soft_reset()
        
        # Wait until button pressed
        if not running:
            Robot.stop()
            sleep(0.01)
            continue  # ← Go back to top of loop
        
        # Running - do path update
        path.update()
        sleep(0.01)



