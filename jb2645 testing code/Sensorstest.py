from machine import Pin, ADC
from general_component_classes import *
from general_component_classes import *
from line_following import *
from rover_class_creation import *
from machine import Pin
import time
from utime import sleep
from utime import sleep
from machine import Pin, SoftI2C, I2C

from libs.tcs3472_micropython.tcs3472 import tcs3472

#from libs.DFRobot_TMF8x01.DFRobot_TMF8x01 import DFRobot_TMF8801, DFRobot_TMF8701    #shouldnt have this sensor?


motorL = Motor(dirPin=4, PWMPin=5)#check values later
motorR = Motor(dirPin=7, PWMPin=6)
sensors = Optocoupler(12, 21, 14, 20)
verticalservo = Servo(13)
horizontalservo = Servo(15)
Robot = Rover(motorL, motorR, sensors, horizontalservo, verticalservo)
follower = LineFollow(Robot, sensors)
while True:
    print(sensors.getvalues())
    sleep(1)
    