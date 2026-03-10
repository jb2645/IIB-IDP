def turnleft1(self):               #code for turning 
        turned = False
        motorstarted = False
        slowflag = False
        nearlyturned = False
        
        while turned == False:                                          #keeps turning until detects it is on line. 
            if slowflag == False and motorstarted == False:        #flags to make sure motor instructions are only input once
                self.right.Forward(85)
                self.left.Reverse(75)
                motorstarted = True
                sleep(0.1)
            
            sensorvalues = self.Optocoupler.getvalues()          #finds the sensor values
            
            if sensorvalues[0] == 1:                   #slows down turn when outer sensor detects line desired 
                if slowflag == False:
                    sleep(0.08)
                    slowflag = True
                    self.right.Forward(60)
                    self.left.Reverse(60)
        
            if sensorvalues[2] == 1:
                sleep(0.1)
                nearlyturned = True
                
            if sensorvalues[3] == 1 and sensorvalues[0] == 0 and nearlyturned == True:    #outer left past line, inner right has hit line so it is turned, inner left having previously gone over line
                sleep(0.2)
                turned = True
            #sleep(0.05)
            
            

    def turnright1(self):
        turned = False
        motorstarted = False
        slowflag = False
        nearlyturned = False
        
        while turned == False:
            if slowflag == False and motorstarted == False:
                self.left.Forward(85)
                self.right.Reverse(75)
                motorstarted = True
                sleep(0.1)
            
            sensorvalues = self.Optocoupler.getvalues()          #finds the sensor values
            
            if sensorvalues[1] == 1:                   #slows down turn when outer sensor detects line desired 
                if slowflag == False:
                    sleep(0.08)
                    slowflag = True
                    self.left.Forward(60)
                    self.right.Reverse(60)
        
            if sensorvalues[3] == 1:#to discard any anomalous readins in LH sensor
                sleep(0.1)
                nearlyturned = True
                
            if sensorvalues[2] == 1 and sensorvalues[1] == 0 and nearlyturned == True:
                sleep(0.2)
                turned = True
                