
'''def main():
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    bays = [1,2,6,7]
    pos = Position(grid)
=======
def main():
    grid = [(3,1),(2,0),(3,1),(2,0),(2,5),(7,6),(9,5),(9,5)]
    bays = [1,2,6,7]
    pos = Position(grid)##
>>>>>>> Stashed changes

    
    left_motor = Motor(dirPin=4, PWMPin=5)#check values later
    right_motor = Motor(dirPin=6, PWMPin=7)

    #sensors = LineSensors(['''pin1,pin2,pin3,pin4'''])
    #sensors = Optocoupler(6, 7, 8, 9)      #check actual order of gpio pins
    
    drive = MainDrive(left_motor, right_motor)
    drive = Rover(left_motor, right_motor, sensors) # This will need to be updated later when rover class completed
    
    path = Path_LFT(drive, sensors)
    
    follower = LineFollow(drive, sensors)
    
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
                    drive.turnleft()
                    pos.turn_end(1)
                    
                else:
                    pos.turn_end(0)
                    drive.turnright()
                    #turn right 

        time.sleep(0.01)
        
#main()

'''