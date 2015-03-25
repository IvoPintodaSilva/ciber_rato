#Ivo Silva, 64833
#Ricardo Martins, 64401

from croblink import *

from math import *
from tree_search import *



class Pontos(SearchDomain):
    def __init__(self,connections, coordinates):
        self.connections = connections
        self.coordinates = coordinates
    def actions(self,ponto):
        actlist = []
        print "CONNECT",self.connections
  
        for (C1,C2, D) in self.connections:
            
            if (str(C1) == str(ponto)):
                actlist += [(C1,C2)]
            elif (str(C2) == str(ponto)):
                actlist += [(C2,C1)]
        return actlist 
    def result(self,state,action):
        (C1,C2) = action
        if (C1 == state):
            return C2
    def cost(self,state,action):
        (C1,C2) = action
        if (str(C1) != str(state)):
            return None
        for (x,y,D) in self.connections:
            if (str(x) == str(C1) and str(y) == str(C2)) or (str(x) == str(C2) and str(y) == str(C1)):
                return D





class MyRob(CRobLink):
    turn = 'center'
    turnOld = 'center2'
    lastPos = 0
    myDict = {}
    contourAngle = 0
    startTurning = (0,0)
    positions = []
    positionsOrdered = []
    connections = []
    def run(self):
        if rob.status!=0:
            print "Connection refused or error"
            quit()

        state='stop'
        stoppedState='run'

        self.start_saved = False
        self.prev_ground = 99

        self.counter = 0


        while True:
            self.readSensors()

            if (self.measures.groundReady):
                if self.measures.ground !=self.prev_ground:
                    print state,"ground=",self.measures.ground
                    self.prev_ground = self.measures.ground
 
            if self.measures.endLed:
                print self.robName + " exiting"
                quit()

            if (state=='stop' and self.measures.start):
                state=stoppedState

            if (state!='stop' and self.measures.stop):
                stoppedState=state
                state='stop'

            if (state=='run'):
                if not self.start_saved:
                    if self.measures.gpsReady:
                        self.start_pos = (self.measures.x,self.measures.y)
                        self.start_saved = True
                if self.measures.returningLed:
                    state='return'
                if self.measures.visitingLed:
                    self.setVisitingLed(False)
                    self.setReturningLed(True)  
                    ##################################################	
                    self.positions += [(self.measures.x, self.measures.y)]
                    self.myDict[str(self.positions[len(self.positions)-1])] = self.positions[len(self.positions)-1]
                    self.connections += [((str(self.positions[len(self.positions) -1])),(str(self.positions[len(self.positions) - 2])),1)]
                    p = SearchProblem(Pontos(self.connections, self.myDict),(self.measures.x,self.measures.y),self.start_pos)
                    t = SearchTree(p,'uniform')
                    self.positionsOrdered = t.search()

                  
                    ###################################################
                    state='return'
                if not self.measures.visitingLed and \
                   not self.measures.returningLed and \
                   self.measures.groundReady and self.measures.ground==0:
                    self.setVisitingLed(True)
                    print self.robName + " visited target area"
                else:
                    (lPow,rPow) = self.determineAction("run")
                    self.driveMotors(lPow,rPow)

            if (state=='return'):
                if self.measures.groundReady and self.measures.ground==1:
                    self.finish()
                    print self.robName + " found home area"
                elif self.measures.gpsReady and \
                     dist((self.measures.x,self.measures.y),self.start_pos)<0.5:
                    self.finish()
                    print self.robName + " really close to start position"
                else:
                    (lPow,rPow) = self.determineAction("return")
                    self.driveMotors(lPow,rPow)

    def determineAction(self,state):

        flag = 0
        i = 0
        for a in self.positions:
            if dist(a, (self.measures.x, self.measures.y)) < 1.5 and flag == 0:
                flag = 1
            if flag == 0:
                i+=1

        if state == 'run':
            if len(self.positions) != 0:
                if dist((self.measures.x, self.measures.y), self.positions[len(self.positions) - 1]) > 3 and flag == 0:
                    self.positions += [(self.measures.x, self.measures.y)]
                    self.myDict[str(self.positions[len(self.positions)-1])] = self.positions[len(self.positions)-1]
                    self.connections += [((str(self.positions[len(self.positions) -1])),(str(self.positions[self.lastPos])),1)]
                    self.lastPos = len(self.positions)-1
                elif dist((self.measures.x, self.measures.y), self.positions[self.lastPos]) > 3 and flag == 1:
                    print "repetido"
                    self.connections += [((str(self.positions[len(self.positions) -1])),(str(self.positions[i])),1)]
                    self.lastPos = i
            else:
                self.positions += [(self.measures.x, self.measures.y)]
                self.myDict[str(self.positions[0])] = self.positions[0]

        print "lastPos", self.lastPos
        center_id = 0
        left_id = 1
        right_id = 2
        back_id = 3
        center = left = right = back = 0






        if self.measures.irSensorReady[left_id]:
            left = self.measures.irSensor[left_id]
        if self.measures.irSensorReady[right_id]:
            right = self.measures.irSensor[right_id]
        if self.measures.irSensorReady[center_id]:
            center = self.measures.irSensor[center_id]
        if self.measures.irSensorReady[back_id]:
            back = self.measures.irSensor[back_id]

        beaconReady = self.measures.beaconReady
        if(beaconReady):
            (beaconVisible,beaconDir) =  self.measures.beacon

        if (self.measures.groundReady):
            ground = self.measures.ground
        if (self.measures.collisionReady):
            collision = self.measures.collision

      
        lPow=0.15
        rPow=0.15

        follow = False



        if state == 'run' and beaconReady and beaconVisible:
            self.turn = 'center2'


        rotate = 0        

        if right > 2 and left > 2 and center < 2:
            rotate = 1
            lPow = 0.15
            rPow = 0.15
        elif center > 2.5 and left > 2:
            rotate = 1
            lPow = 0.7
            rPow = -0.7
        elif center > 2.5 and right > 2:
            rotate = 1
            lPow = -0.7
            rPow = 0.7
        elif right > 2.5:
            rotate = 1
            lPow = 0.07
            rPow = 0.15
        elif left > 2.5:
            rotate = 1
            lPow = 0.15
            rPow = 0.07
        

        


        if (center > 1.5 and left > 0.5 and right > 0.5 and self.turn == 'center') :
            self.turnOld = 'center'
            self.position = (self.measures.x, self.measures.y)
            if(self.counter % 100 < 50):
                self.contourAngle = self.measures.compass
                self.turn = 'cleft'
                lPow=-0.15
                rPow=0.15
            else:
                self.contourAngle = self.measures.compass
                self.turn = 'cright'
                lPow=0.15
                rPow=-0.15

        elif (self.turn == 'center2' or collision) and rotate == 0:
            if collision:
                if self.turnOld == 'right':
                    lPow = -0.15
                    rPow = 0.15
                else:
                    lPow = 0.15
                    rPow = -0.15



            elif state == 'run' and beaconReady and beaconVisible:
                print "run to beacon"
                follow = True
                target_dir = beaconDir
    
                if follow and target_dir>20.0:
                    lPow=0.0
                    rPow=0.1
                elif follow and target_dir < -20.0:
                    lPow=0.1
                    rPow=0.0
                else:
                    lPow=1
                    rPow=1

            elif left > 1 and center > 1 and state == 'run':
                lPow = 0.1
                rPow = -0.1
                self.contourAngle = self.measures.compass
                self.turn = 'cright'
                self.turnOld = 'center2'
            elif center >1 and right >1 and state == 'run':
                lPow = -0.1
                rPow = 0.1
                self.contourAngle = self.measures.compass
                self.turn = 'cleft'
                self.turnOld = 'center2'




            elif state=="return" and self.measures.gpsReady \
                   and self.measures.compassReady:
                print "return to home"
                follow = True
  

                ###############################################################################

        
                if self.positionsOrdered != []:
                    xy = self.positionsOrdered[0]
                    (x,y) = self.myDict[str(xy)]
                    
                else:
                    x = self.start_pos[0]
                    y = self.start_pos[1]


                print x
                print y
                print '-----------------'
                dx = x - self.measures.x
                dy = y - self.measures.y


                if self.measures.x < x +2 and self.measures.x > x -2 and self.measures.y < y+2 and self.measures.y > y-2 and len(self.positionsOrdered) - 1 >= 0:
                    self.positionsOrdered[0:1] = []


                abs_target_dir = atan2(dy,dx)*180/3.141592

                target_dir = abs_target_dir-self.measures.compass
                if target_dir > 180:
                    target_dir -= 360
                elif target_dir < -180:
                    target_dir += 360

                
                if right > 1.5:
                    lPow = 0.07
                    rPow = 0.15
                elif left > 1.5:
                    lPow = 0.15
                    rPow = 0.07
                elif follow and target_dir>20.0:
                    lPow=0.0
                    rPow=0.1
                elif follow and target_dir < -20.0:
                    lPow=0.1
                    rPow=0.0
                else:
                    lPow=1
                    rPow=1
            else:
                lPow = 0.15
                rPow = 0.15


        


        elif self.turn == 'cright' and rotate == 0:
            
            if center > 1:
                lPow = 0.5
                rPow = -0.5
            else:
                lPow = 1
                rPow = 1
                self.turn = 'left'
                self.turnOld = 'cright'

        elif self.turn == 'cleft' and rotate == 0:
            if center > 1:
                lPow = -0.5
                rPow = 0.5
            else:
                lPow = 1
                rPow = 1
                self.turn = 'right'
                self.turnOld = 'cleft'

        
        elif self.turn == 'right' and rotate == 0:
            if collision:
                lPow = 0.15
                rPow = -0.15
            elif center > 1 and right > 1 and left < 1:
                lPow = 0
                rPow = 0
                self.turn = 'cleft'
                self.turnOld = 'right'
            elif center > 1 and left > 1 and right < 1:
                lPow = 0
                rPow = 0
                self.turn = 'cright'
                self.turnOld = 'right'
            elif right > 1:
                lPow = 0.15
                rPow = 0.15
                self.searchBeacon = True
            elif right < 1 or left > 1:
                lPow = 0.15
                rPow = 0
            else:
                lPow = 0
                rPow = 0
                if self.contourAngle - 7.5 < self.measures.compass and self.contourAngle +7.5 > self.measures.compass:
                    self.turn = 'center2'
                    self.turnOld = 'right'


        elif self.turn == 'left' and rotate == 0:
            if collision:
                lPow = -0.15
                rPow = 0.15
            elif center > 1 and right > 1 and left < 1:
                lPow = 0
                rPow = 0
                self.turn = 'cleft'
                self.turnOld = 'left'
            elif center > 1 and left > 1 and right < 1:
                lPow = 0
                rPow = 0
                self.turn = "cright"
                self.turnOld = "left"
            elif left > 1:
                lPow = 0.15
                rPow = 0.15
                self.searchBeacon = True
            elif left < 1 or right > 1:
                lPow = 0
                rPow = 0.15
            else:
                lPow = 0
                rPow = 0
                if self.contourAngle - 7.5 < self.measures.compass and self.contourAngle+7.5 > self.measures.compass:
                    self.turn = 'center2'
                    self.turnOld = 'left'
                for a in self.positions:
                    (xa, ya) = a
                    (xb, yb) = self.positions[len(self.positions)-1]
                    if xa != xb or ya != yb:
                        if dist(self.positions[len(self.positions)-1],a) < 0.5 and self.turn != 'center' and self.turn != 'center2':
                            rPow = 0.15
                            lPow = -0.15
                            self.turn = 'center'
       
        self.counter += 1
        return lPow,rPow

def dist(p,q):
    (px,py) = p
    (qx,qy) = q
    return sqrt((px-qx)**2 + (py-qy)**2)

rob=MyRob("AA",1,"localhost")

rob.run()


