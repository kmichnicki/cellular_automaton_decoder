import random
from copy import deepcopy
from visual import *
from time import sleep


class toric:

    def __init__(self):
        self.size=8 #10 by 10 stabilizers which means 200 qubits
        self.gibbs=10  #inverse temperature
        self.prob=.05 #base probability of an error
        self.Hqubits=[] #the array that holds whether an error occurs on a qubit that is horizontal to the stabilizer vertices
        self.Vqubits=[] #the array that holds whether an error occurs on a qubit that is vertical to the stabilizer vertices
        
        self.CA1=[] # [N,E,S,W]
        self.CA2=[]
        
    #Sets up the array and sets values to zero
    def initializeQubits(self):
    
        for x in range(self.size):
            self.Hqubits.append([])
            self.Vqubits.append([])
            for y in range(self.size):
                self.Hqubits[x].append(0)
                self.Vqubits[x].append(0)

    def checkStab(self,i,j): #checks the parity of a given stabilizer
        p=(self.Hqubits[((i-1)%self.size)][j]
           +self.Hqubits[i][j]
           +self.Vqubits[i][((j-1)%self.size)]
           +self.Vqubits[i][j])
        return p%2      
        #for x in self.qubits:
         #   if (x[0]==i and x[1]==j) or (x[2]==i and x[3]==j):
          #      p=p+x[4]

    
                    
                
    #flips a bit with a probability self.gibbs**(change in energy)           
    def applyError(self):
        
        n=0
        H=[]
        V=[]
        for x in range(self.size):
            H.append([])
            V.append([])
            for y in range(self.size):
                H[x].append(self.Hqubits[x][y])
                V[x].append(self.Vqubits[x][y])
            
        for x in range(self.size):
            for y in range(self.size):
                
                rand=random.random()# generate the random number
                
                #count the number of defect to the left and right of a qubit
                horiz=self.checkStab(x,y)+self.checkStab((x+1)%self.size,y) #add up anyons to the right and left of the qubit
                #if there are no defects then applying a pauli increases the energy by 2, if there is 1 defect the energy increases by 0 and 2 defects energy decreases by 2.
                if horiz==0: #no neighboring defects
                    if rand<self.prob*(self.gibbs**2):
                        H[x][y]=(self.Hqubits[x][y]+1)%2
                elif horiz==1: #one neighboring defect
                    if rand<self.prob*self.gibbs**1:
                        H[x][y]=(self.Hqubits[x][y]+1)%2
                else:           #two neighboring defects
                    if rand<self.prob:
                        H[x][y]=(self.Hqubits[x][y]+1)%2

                rand=random.random()    
                vert=self.checkStab(x,y)+self.checkStab(x,(y+1)%self.size)
                if vert==0:
                    if rand<self.prob*self.gibbs**2:
                        V[x][y]=(self.Vqubits[x][y]+1)%2
                elif vert==1:
                    if rand<self.prob*self.gibbs**1:
                        V[x][y]=(self.Vqubits[x][y]+1)%2
                else:
                    if rand<self.prob:
                        V[x][y]=(self.Vqubits[x][y]+1)%2
        self.Hqubits=H
        self.Vqubits=V
            

#Each cell has four flags:north, east, south, west. The cell looks east and if it sees west, it flags west. It looks east and sees west it flags west,etc...


    def initializeCA(self):
        for x in range(self.size):
            self.CA1.append([])
            self.CA2.append([])
            for y in range(self.size):
                self.CA1[x].append([0,0,0,0])
                self.CA2[x].append([0,0,0,0]) #x and y label the stabilizer

    def incrementCA(self): #reduces the value of arrows after each time step. Don't actually use this. It was for testing.
        CA=[]
        for x in range(self.size):
            CA.append([])
            for y in range(self.size):
                CA[x].append([0,0,0,0])
                for i in range(4):
                    if self.CA1[x][y][i]: CA[x][y][i]=(self.CA1[x][y][i]-1)%3

        self.CA1=CA
                                        
    def CAstep3(self,destructionprobability=0):
        """This CA shoots out arrows in all directions in a single stream, without fanning out. That is it shoots out a line of arrows."""
        #initializes a temp array so that changes made in the correction step can be stored here without affecting changes in the same time step.

        aT=destructionprobability#an arrow/wave propagates with a probability 1-aT, 1-arrowThreshold 

        temp=[]
        for x1 in range(self.size):
            temp.append([])
            for y1 in range(self.size):
                temp[x1].append([0,0,0,0])

        
                
        
        
        for x in range(self.size):
            for y in range(self.size):

                
                #if northern-neighbor is marked south then cell is marked south

                #the if else code below if uncommented would make it so that arrows propagate with a fixed probability. This limits their range. 
                if random.random()>aT: #only lets the arrows propagate with a fixed probability
                    temp[x][y][2]=self.CA1[x][((y+1)%self.size)][2]
                else:
                    temp[x][y][2]=0
                                       
                
                #if eastern-neighbor is marked west then cell is marked west
                if random.random()>aT:
                    temp[x][y][3]=self.CA1[((x+1)%self.size)][y][3]
                else:
                    temp[x][y][3]=0
                                    
                
                #if southern-neighbor is marked north then cell is marked north
                if random.random()>aT:
                    temp[x][y][0]=self.CA1[((x)%self.size)][((y-1)%self.size)][0]
                else:
                    temp[x][y][0]=0
                

                #if western-neighbor is marked east then cell is marked east
                if random.random()>aT:
                    temp[x][y][1]=self.CA1[((x-1)%self.size)][y][1]
                else:
                    temp[x][y][1]=0
                                        
               

                #bounce perpendicular beams off of each other. An arrow has a value of 2,1 or 0. It starts off with a value of 2 and when it bounes once it gets a 1 and then a second bounce destroys the arrow.
                #If the arrows are not, empty/non-existent or (north and south) or (east and west): then the arrows bounce off of each other and decrement
                if ((temp[x][y][0] and temp[x][y][1])
                    or (temp[x][y][1] and temp[x][y][2])
                    or (temp[x][y][2] and temp[x][y][3])
                    or (temp[x][y][3] and temp[x][y][0])):
                    temp[x][y]=[temp[x][y][2],temp[x][y][3],temp[x][y][0],temp[x][y][1]] #flip the arrows
                    for b in [0,1,2,3]:
                        if temp[x][y][b]: temp[x][y][b]=temp[x][y][b]-1
                        
                      #delete this after you have tested that arrows bounce properly. Bad version of the function  
##                if temp[x][y][0]==2 and temp[x][y][1]==2 and self.checkStab(x,y)==0:
##                    temp[x][y]=[0,0,temp[x][y][0]-1,temp[x][y][1]-1]
##                elif temp[x][y][1]==2 and temp[x][y][2]==2 and self.checkStab(x,y)==0:
##                    temp[x][y]=[temp[x][y][2]-1,0,0,temp[x][y][1]-1]
##                elif temp[x][y][2]==2 and temp[x][y][3]==2 and self.checkStab(x,y)==0:
##                    temp[x][y]=[temp[x][y][2],temp[x][y][3],0,0]
##                elif temp[x][y][3]==2 and temp[x][y][0]==2 and self.checkStab(x,y)==0:
##                    temp[x][y]=[0,temp[x][y][3]-1,temp[x][y][0]-1,0]
                   
                if self.checkStab(x,y)==1: #if any of the stabilizers are marked then the cell shouts, that is, violated stabilizers always create waves.
                    temp[x][y]=[2,2,2,2]
                    
                if x==(self.size-1) and y==(self.size-1):
                    self.CA1=temp #now that the calculation is done, update the state of the cellular automata
               

        
        
        
        
    
    def CAcorrect(self):

        #create temporary array
        V=[]
        H=[]
        for x in range(self.size):
            V.append([])
            H.append([])
            for y in range(self.size):
                V[x].append(self.Vqubits[x][y])
                H[x].append(self.Hqubits[x][y])
                
        for x in range(self.size):
            
            for y in range(self.size):
                if self.checkStab(x,y)==1:
                    n=self.CA1[x][(y+1)%self.size][2] #is there a defect north, east, etc...
                    e=self.CA1[(x+1)%self.size][y][3]
                    s=self.CA1[x][(y-1)%self.size][0]
                    w=self.CA1[(x-1)%self.size][y][1]

                    #quasi-particles are only allowed to move up and to the right. This is to prevent them from getting trapped in cycles.
                    
                    if (n>s and e<=w): #go north
                        V[x][y]=(self.Vqubits[x][y]+1)%2
                        
                    elif (e>w and n<=s): #go east
                        H[x][y]=(self.Hqubits[x][y]+1)%2
                        
                    elif (n>s and e>w): #choose between north and east when there is ambiguity
                        if random.random()<.5:
                            V[x][y]=(self.Vqubits[x][y]+1)%2
                        else:
                            H[x][y]=(self.Hqubits[x][y]+1)%2

                    else:
                        pass
##                    elif (e>w and s>n): #choose between east and south
##                        if random.random()<.5:
##                            H[x][y]=(self.Hqubits[x][y]+1)%2
##                        else:
##                            pass
##                            #V[x][(y-1)%self.size]=(self.Vqubits[x][(y-1)%self.size]+1)%2
##                        
##                    elif (w>e and s>n): #choose between south and west
##                        if random.random()<.5:
##                            pass#V[x][(y-1)%self.size]=(self.Vqubits[x][(y-1)%self.size]+1)%2
##                        else:
##                            pass#H[(x-1)%self.size][y]=(self.Hqubits[(x-1)%self.size][y]+1)%2
##                        
##                    elif (n>s and w>e): #choose between west and north
##                        if random.random()<.5:
##                            pass#H[(x-1)%self.size][y]=(self.Hqubits[(x-1)%self.size][y]+1)%2
##                        else:
##                            V[x][y]=(self.Vqubits[x][y]+1)%2
##                        
##                    else:
##                        pass
        self.Hqubits=H
        self.Vqubits=V

        
                    
    #This is the decoder section. It uses the Bravyi-Haah RG decoder. 
    def checkForAnyErrors(self):
        flag=0
        for x in range(self.size):
            for y in range(self.size):
                if self.checkStab(x,y):
                    flag=1
                    break
            if flag==1: break

        return flag
    
    def checkForLogicalErrors(self):
        """If there are any logical errors, vertical or horizontal, then return a 1 otherwise return 0"""
        if self.checkForAnyErrors():
            print("error, the decoder is not done")
            self.drawAll()
            exit()
        flag1=0
        flag2=0
        for x in range(self.size):
            flag1=(flag1+self.Vqubits[x][0])%2
            flag2=(flag2+self.Hqubits[0][x])%2

        if flag1 or flag2:
            return 1
        else:
            return 0
            
                


    #the RG decoder at work
    def findAllNeighbors(self,anyonList=[],scale=1):
        
        anyonTemp=[]
        for var in anyonList:
            for x in range(self.size):
                for y in range(self.size):
                    if (self.checkStab(x,y)
                        and ((min((x-var[0])%self.size,(var[0]-x)%self.size)+min((y-var[1])%self.size,(var[1]-y)%self.size)) <= scale)
                        and ([x,y] in anyonTemp)!=True):
                        anyonTemp.append([x,y])
        if len(anyonTemp)!=len(anyonList):
            
            return self.findAllNeighbors(anyonTemp,scale)
        else:
            return deepcopy(anyonTemp)

    def destroyPair(self,pos1,pos2):
        x=pos1[0]
        y=pos1[1]
        u=pos2[0]
        v=pos2[1]
        if (x-u)%self.size<(u-x)%self.size: # u move to the right
            for n in range(abs((x-u)%self.size)):
                self.Hqubits[(u+n)%self.size][v]=(self.Hqubits[(u+n)%self.size][v]+1)%2
        elif x!=u: # move to the left
            for n in range(abs((u-x)%self.size)):
                self.Hqubits[(u-1-n)%self.size][v]=(self.Hqubits[(u-1-n)%self.size][v]+1)%2
        else: #equal distance either way so guess.
            if random.random()>1/2:
                for n in range(abs((x-u)%self.size)):
                    self.Hqubits[(u+n)%self.size][v]=(self.Hqubits[(u+n)%self.size][v]+1)%2 
            else:
                for n in range(abs((u-x)%self.size)):
                    self.Hqubits[(u-1-n)%self.size][v]=(self.Hqubits[(u-1-n)%self.size][v]+1)%2
        
        if (y-v)%self.size<(v-y)%self.size:
            for n in range(abs((y-v)%self.size)):
                self.Vqubits[x][(v+n)%self.size]=(self.Vqubits[x][(v+n)%self.size]+1)%2
                
        elif y!=v:
            for n in range(abs((v-y)%self.size)):
                self.Vqubits[x][(v-1-n)%self.size]=(self.Vqubits[x][(v-1-n)%self.size]+1)%2
        else:
            if random.random()>1/2:
                for n in range(abs((y-v)%self.size)):
                    self.Vqubits[x][(v+n)%self.size]=(self.Vqubits[x][(v+n)%self.size]+1)%2 
            else:
                for n in range(abs((v-y)%self.size)):
                    self.Vqubits[x][(v-1-n)%self.size]=(self.Vqubits[x][(v-1-n)%self.size]+1)%2
            #print('ok')
    
    
    def RGdecoder(self):
        scale=1
        group=[]
        
        while scale<4*self.size:
            for x in range(self.size):
                for y in range(self.size):
                    if self.checkStab(x,y):
                        group=self.findAllNeighbors([[x,y]],scale)
                       
                        #destroy the group=[[x,y]] of neighboring anyons
                        
                        if len(group)%2!=1: 
                            for var in range(int(len(group)/2)):
                                
                                self.destroyPair(group[2*var],group[2*var+1])
                            
                            
            scale=2*scale

                    
    def countAnyons(self):
         count=0
         for x in range(self.size):
             for y in range(self.size):
                 count=count+self.checkStab(x,y)
         return count
        
    #sphere(pos=vector(-1,0,0), radius=.5, color=color.green)
    

    def drawDefects(self):
       
        
        for x in range(self.size):
            for y in range(self.size):
                if self.checkStab(x,y)==1:
                    sphere(pos=vector(x-.5*self.size,y-.5*self.size,0), radius=.15, color=color.red)
                else:
                    sphere(pos=vector(x-.5*self.size,y-.5*self.size,0), radius=.15, color=color.blue)
              

    def drawErrors(self):
        for x in range(self.size):
            for y in range(self.size):
                if self.Hqubits[x][y]==1:
                    sphere(pos=vector(((x+.5)%self.size)-.5*self.size,y-.5*self.size,0), radius=.1, color=color.green)
                if self.Vqubits[x][y]==1:
                    sphere(pos=vector(x-.5*self.size,((y+.5)%self.size)-.5*self.size,0), radius=.1, color=color.green)

    def drawVectors(self):
        
        for x in range(self.size):
            for y in range(self.size):
                
                if self.CA1[x][y][0]>0: #there is an arrow pointing north
                    arrow(pos=vector((x-.5*self.size),(y-.5*self.size),0), axis=vector(0,.45,0), color=color.white)
                else: arrow(pos=vector((x-.5*self.size),(y-.5*self.size),0), axis=vector(0,.45,0), color=color.black)
                
                if self.CA1[x][y][1]!=0: #there is an arrow pointing east
                    arrow(pos=vector(x-.5*self.size,y-.5*self.size,0), axis=vector(.45,0,0), color=color.white)
                else: arrow(pos=vector(x-.5*self.size,y-.5*self.size,0), axis=vector(.45,0,0), color=color.black)
                
                if self.CA1[x][y][2]!=0: #there is an arrow pointing south
                    arrow(pos=vector(x-.5*self.size,y-.5*self.size,0), axis=vector(0,-.45,0), color=color.white)
                else: arrow(pos=vector(x-.5*self.size,y-.5*self.size,0), axis=vector(0,-.45,0), color=color.black)
                if self.CA1[x][y][3]!=0: #there is an arrow pointing north
                    arrow(pos=vector(x-.5*self.size,y-.5*self.size,0), axis=vector(-.45,0,0), color=color.white)
                else: arrow(pos=vector(x-.5*self.size,y-.5*self.size,0), axis=vector(-.45,0,0), color=color.black)

    def drawAll(self,lag=0):
       
        for obj in scene.objects: #this erases earlier pictures so that you don't see a superposition of the entire history of the CA
            obj.visible=0
        
        self.drawDefects()
        self.drawErrors()
        self.drawVectors()
        if lag!=0:
            sleep(lag)

#CAvideo just shows an image, using Vpython, for each time step of the CA decoder and runs for 1000 time steps
def CAvideo(s=4): 
    t=toric()
    t.size=s
    t.initializeQubits()
    t.initializeCA()
    t.prob=0
    t.prob=0.0005
    t.applyError()
    t.gibbs=1
    rate(20)
    #mysphere=sphere(pos=[-1,0,0],radius=.1, color=color.red)
    #mysphere1=sphere(pos=[0,0,0],radius=.1, color=color.red)
    for n in range(1000):
        t.applyError()
        #t.CAstep3()
        #if n>-1: t.drawAll(5)
        
        #t.CAcorrect()
        #mysphere.pos[1]=mysphere.pos[1]+.001
        
        if(n==20): t.drawAll(10) #take a snapshot at this time step
        
        #if (n%int(t.size/2))==0:
        #        t.incrementCA()
                        
                #t.CA1=deepcopy(t.CA2)



#CAtest() tests the CA decoder at different system sizes and a given error rate.
def CAtest(p=.005):
    print("size,time,prob,gibbs,percent of errors")

    averageover=10
    for size in range(7):
        anyoncount=0
        time=0
        for count in range(averageover):
            t=toric()
            r=deepcopy(t)
            t.size=(2**size)+2
            t.initializeQubits()
            t.initializeCA()
            t.prob=p
            t.gibbs=1
            n=0 #used to decide when to look for decoding errors
            wrong=0
            ticker_threshold=1
            while wrong==0:
                n=n+1
          
                            
                t.applyError()
                t.CAstep3()
                t.CAcorrect()
           

                #this next if statement makes it so that we check for a logical error after more waiting if there are no logical errors.
                #if n==ticker_threshold:
                    #ticker_threshold=2*ticker_threshold
                r=deepcopy(t)
                r.RGdecoder()
                if r.checkForLogicalErrors():
                    wrong=1
                
                if n>60000: #sets the maximum lifetime that I'm willing to check.
                    time=0
                    wrong=1
            time=time+n
            anyoncount=anyoncount+t.countAnyons()
        print(str(t.size)+","+str(float(time)/averageover)+"," +str(t.prob)+"," + str(t.gibbs)+"," + str(float(anyoncount)/(averageover*t.size**2)))


def thresholdTest(size,errorrate): #Applies a CAdecoder repeatedly until there are no defects and then tests for logical errors.
    t=toric()
    r=deepcopy(t)
    t.size=size
    t.initializeQubits()
    t.initializeCA()
    t.prob=errorrate
    t.gibbs=1
    t.applyError()
    n=0
    while t.checkForAnyErrors() and n<10000:
        t.CAstep3(1/t.size)
        t.CAcorrect()
        n=n+1
    r=deepcopy(t)
    r.RGdecoder()
    #print("error rate: "+str(errorrate)+", system size: "+str(size)+", time to correct: "+str(n)+", Logical error: "+ str(r.checkForLogicalErrors()))
    return(float(r.checkForLogicalErrors()))





def testDecoder(): #Gives averages  of decoding success rate against one time noise. 
    DATA=[]
    for n in range(0,2): #system size n+4
        for r in range(0,20):
            DATA.append([20*n+20,float(.1-.005*r),float(0.0)])

    m=1
    while m<1000:
        for x in range(len(DATA)):
            DATA[x][2]=thresholdTest(DATA[x][0],DATA[x][1])+DATA[x][2]
        m=m+1
    print("system size, error rate, decoding success rate")
    for x in range(len(DATA)):
        print(str(DATA[x][0])+","+str(DATA[x][1])+","+str(DATA[x][2]/m))

#testDecoder()
#CAvideo(20)        
#CAtest()   
#size=10     

#These next four lines run statistics on the memory lifetime. It averages 10 runs.
p=.0128
for x in range(6):
    CAtest(p)
    p=p/2

