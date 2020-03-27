import serial
import numpy as np
import matplotlib.pyplot as plt
import re
from timeit import default_timer as timer
from serialDataIO import ReadLine
def makeFig(): #Create a function that makes our desired plot
    plt.ylim(0,90)                                 #Set y min and max values
    plt.title('My Live Streaming Sensor Data')      #Plot the title
    plt.grid(True)                                  #Turn the grid on
    plt.ylabel('Signal')                            #Set ylabels
    plt.plot(Signal, 'ro-')       #plot the temperature
    plt.legend(loc='upper left')                    #plot the legend

Signal = []

arduinoData = serial.Serial('com6', 9600) #Creating our serial object named arduinoData

aReadline = ReadLine(arduinoData)
count = 0
plot = False



serialStrings = []
countNmeasures = True

count = 0
print("beginning data aquisition")
while True: # While loop that loops forever
    #while (arduinoData.inWaiting()==0): #Wait here until there is data
     #   pass #do nothing
    if count == 0:
        start = timer()
        print("Data is being recieved")
    #arduinoString = arduinoData.read(size=28) #read the line of text from the serial port
    arduinoString = aReadline.readline()
    arduinoString = str(arduinoString)

    if plot:
        try:
            dataArray = arduinoString.split(':')
            data = re.sub('[^0-9\.]', '', dataArray[-1])
            littleSignal = float(data)
            Signal.append(littleSignal)  # Building our pressure array by appending P readings
            makeFig()  # Call drawnow to update our live graph
            plt.pause(.000001)  # Pause Briefly. Important to keep drawnow from crashing
            count = count + 1
            if len(Signal) > 50:
                Signal.pop(0)  # This allows us to just see the last 50 data points

        except:
            print("could not convert serial data to floating value: " + str(arduinoString))

    if countNmeasures:
        count += 1
        if count == 720:
            end = timer()
            break
        if (count%72) == 0:
            print(count/72)

print (end-start)

