# Main Code
from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
import time
from utime import sleep


running = True
last_press_time = 0
DEBOUNCE_MS = 200   # debounce delay in milliseconds

def button_pressed(pin):
    global running, last_press_time

    now = time.ticks_ms()

    # Debounce check
    if time.ticks_diff(now, last_press_time) > DEBOUNCE_MS:
        if not running:      # Only allow start once
            running = True
            print("STARTED")

    last_press_time = now


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
    pos = Position(grid)
    
    path = Path_LFT(Robot, sensors)
    
    # Wait until button pressed
    while not running:
        Robot.stop()
        time.sleep(0.01)

    # Main loop
    while running:

        event = sensors.junction_detection()
        path.update()
        
        
        if pos.state == "CLEAR":
            follower.adjust()
            print("Clear")
            
        elif pos.state == "JUNCTION":
            nodestate = None
            if path.state != "LEAVING_START":
                nodestate = pos.on_node()
            #Detects position and if turn required it will turn
            
            if nodestate == "TURN":
                path.turn = True
                left_value, right_value = sensors.read_junction()

                if left_value > right_value:
                    pos.turn_end(1)
                else:
                    pos.turn_end(0)

        time.sleep(0.01)