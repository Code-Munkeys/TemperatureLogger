# Designed and Developed by Franz Ayestaran - http://franz.ayestaran.co.uk

# You may use this code in your own projects and upon doing so, you the programmer are solely
# responsible for determining it's worthiness for any given application or task. Here clearly
# states that the code is for learning purposes only and is not guaranteed to conform to any
# programming style, standard, or be an adequate answer for any given problem.

import matplotlib.pyplot as plt

# Open File
file = open("TemperatureGraph.csv", "r")

# Transforms CSV file data into arrays xAxis and yAxis that are required for graph plotting
xAxis = []; yAxis = []; index = 0
unitType = ""

for data in file:
    data = data.replace("\n", "")
    data = data.split(",")
    
    temperature = data[0] + chr(176) #Add the degrees symbol to the retrieved data
    unitType = data[1]
    datetime = data[4]
    
    #Filter out the CSV header names
    if temperature != "temperature" + chr(176):
    
        #Extract only the time (HH:MM:SS) for the x axis labels
        datetime = datetime[11:19]
    
        xAxis.append(datetime)
        yAxis.append(temperature)
    
    index = index + 1
    
file.close()

plt.plot(xAxis,yAxis, '-o')
plt.title('Temperature Logger Data Graph')
plt.xlabel('Time (HH:MM:SS)')
plt.ylabel('Temperature in degrees ' + unitType)
plt.grid()
plt.show()
