# Designed and Developed by Franz Ayestaran - http://franz.ayestaran.co.uk

# You may use this code in your own projects and upon doing so, you the programmer are solely
# responsible for determining it's worthiness for any given application or task. Here clearly
# states that the code is for learning purposes only and is not guaranteed to conform to any
# programming style, standard, or be an adequate answer for any given problem.

# Raspberry Pi Pico with external RTC

# Usage:
#
# When the Splash screen has displayed for 5 seconds, the User will be presented with a Calibration screen.
# The User can press the GREEN Button to increase and the RED Button to decrease the required temperature adjustment
# amount, when finished the User simply presses the BLUE Button to continue.
#
# When the Temperature screen is displayed the User can perform the following functions via the assigned inputs.
# RED Button: Toggle Logging On / Off, GREEN Button: Toggle °C / °F, BLUE Button: Toggle OLED display On / Off.
# When the OLED Display is in the off state, the Pico onboard LED is illuminated to show the temperature logger is on.
#
# POTENTIOMETER: Interval time <Left 60s> <Center 30s> <Right 15s> (s = seconds)
#
# When the logging CSV file is created and appended to, the filename suffix datetime stamp is set to the following format...
# [temperatureYYYY-MM-DD_HHMMSS.csv]. If no external RTC is installed then an additional random suffix number can be added
# to the filename... [temperatureYYYY-MM-DD_HHMMSS_01234567.csv]
#
# Whenever the logging CSV file is being updated, the red LED will illuminate for half a second. 

import machine
import time
import utime
import random
import binascii
import math
import framebuf
import sys

from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, ADC

adcTemperature = 4
temperatureSensor = machine.ADC(adcTemperature)
temperatureCurrent = 0

#Calibration + / - in degrees centigrade
temperatureCalibration = 0

adcPotentiometer = ADC(Pin(26))

loggingLed = Pin(15, Pin.OUT)

onboardLed = Pin("LED", Pin.OUT)
onboardLed.off()

w = 128
h = 32
unit_type = "C"

OLED_I2C1 = I2C(1, scl=Pin(3), sda=Pin(2), freq=200000)
OLED_I2C1_ADDR = OLED_I2C1.scan()[0]
OLED128X32 = SSD1306_I2C(w, h, OLED_I2C1, OLED_I2C1_ADDR)
print("OLED_I2C1 Addr: " + str(OLED_I2C1_ADDR))

imageBuffer = bytearray (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfc \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\'\xe0\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x0f\x84%\'?x\xe6\xce!-\x9c\x00\x00\x00\x00\x00\x08\x84%(\xa5E\x13\x02}&"\x00\x1a\x00\xc0\x00\t\x84!\x0f\xa5E\xf2\x1e!$>\x00&\x00@\x00\x08\x84!\x08%E\x02\x12!$ \x00@q\xc6\x00\t\x84#\xc7\xa5x\xf7\x9f=\xef\x1e\x00@\x8aI\x00\x08\x84 \x00\x00@\x00\x00\x00\x00\x00\x00@\x8aO\x00\x0b\x84 \x00\x00@\x00\x00\x00\x00\x00\x00@\x8aH\x00\x08\x84 \x00\x00\x00\x00\x00\x00\x00\x00\x00"\x8aI\x00\t\x84 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x1cq\xe6\x00\x08\x84\'\xff\xff\xff\xff\xff\xff\xff\x80\x00\x00\x00\x00\x00\t\x84 \x00\x00\x00\x00\x00\x00\x00\x03\x06\x000\x00\x00\x08\x84 \x00\x00\x00\x00\x00\x00\x00\x01\x8c\x00\x10\x00\x00\x0b\x84 \x00\x00\x00\x00\x00\x00\x00\x01\x8d\xb6\x97l\xbc\x08\x84\'\x80\x00\x00\x00\x00p\x07\x01T\x93T\x94\xa4\x0f\x84"\x0f\x1ey\xcd\x80\x10\x08\x81T\x92X\xf4\x90\x0f\x84"\x10\xa2\x8a&\x00\x10\x08\x81T\x92T\x83\x0c\n\x84"P\xa2\x8b\xe4\x00\x10\x08\x81$\x92R\x91$\x15D"P\xa2\x8a\x04\x00\x10\x08\x83\xae\x7fwa8*\xa4\'\xcf\x1ey\xef\x00\x10\x08\x80\x00\x00\x00\x02\x005d \x00\x02\x08\x00\x00\x10\xc8\x80\x00\x00\x00\x0c\x00*\xa4 \x00\x0e8\x00\x00|\xc7\x00\x00\x00\x00\x00\x00\x1f\xc4 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04?\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
splashScreen = framebuf.FrameBuffer(imageBuffer, 128, 32, framebuf.MONO_HLSB)

buttonBlue = Pin(6, Pin.IN, Pin.PULL_DOWN)
buttonRed = Pin(14, Pin.IN, Pin.PULL_DOWN)
buttonGreen = Pin(10, Pin.IN, Pin.PULL_DOWN)

RTC_EXTERNAL_I2C0_PORT = 0
RTC_EXTERNAL_I2C0_SDA = 20
RTC_EXTERNAL_I2C0_SCL = 21
RTC_EXTERNAL_I2C0_ALARM_PIN = 3

logging = False
index = 0
interval = 0
csvFieldNamesWritten = False
displayOnOff = False

custom_date_dictionary = {}
custom_date_dictionary ['year'] = 2021
custom_date_dictionary ['month'] = 1
custom_date_dictionary ['day'] = 1
custom_date_dictionary ['weekday'] = 1

custom_time_dictionary = {}
custom_time_dictionary ['hour'] = 0
custom_time_dictionary ['min'] = 0
custom_time_dictionary ['sec'] = 0
custom_time_dictionary ['subsec'] = 0

oledLine1 = 1
oledLine2 = 11
oledLine3 = 21

class ds3231(object):
#            13:45:00 Mon 24 May 2021
#  the register value is the binary-coded decimal (BCD) format
#               sec min hour week day month year
    NowTime = b'\x00\x45\x13\x02\x24\x05\x21'
    w  = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    address = 0x68
    start_reg = 0x00
    alarm1_reg = 0x07
    control_reg = 0x0e
    status_reg = 0x0f
    
    def __init__(self,i2c_port,i2c_scl,i2c_sda):
        self.bus = I2C(i2c_port,scl=Pin(i2c_scl),sda=Pin(i2c_sda))

    def set_time(self,new_time):
        hour = new_time[0] + new_time[1]
        minute = new_time[3] + new_time[4]
        second = new_time[6] + new_time[7]
        week = "0" + str(self.w.index(new_time.split(",",2)[1])+1)
        year = new_time.split(",",2)[2][2] + new_time.split(",",2)[2][3]
        month = new_time.split(",",2)[2][5] + new_time.split(",",2)[2][6]
        day = new_time.split(",",2)[2][8] + new_time.split(",",2)[2][9]
        now_time = binascii.unhexlify((second + " " + minute + " " + hour + " " + week + " " + day + " " + month + " " + year).replace(' ',''))
        #print(binascii.unhexlify((second + " " + minute + " " + hour + " " + week + " " + day + " " + month + " " + year).replace(' ','')))
        #print(self.NowTime)
        self.bus.writeto_mem(int(self.address),int(self.start_reg),now_time)
    
    def read_datetime(self):
        t = self.bus.readfrom_mem(int(self.address),int(self.start_reg),7)
        a = t[0]&0x7F  #second
        b = t[1]&0x7F  #minute
        c = t[2]&0x3F  #hour
        d = t[3]&0x07  #week
        e = t[4]&0x3F  #day
        f = t[5]&0x1F  #month
        #print("20%x/%02x/%02x %02x:%02x:%02x %s" %(t[6],t[5],t[4],t[2],t[1],t[0],self.w[t[3]-1]))
        rtc_external_datetime = "20%x-%02x-%02x %02x:%02x:%02x" %(t[6],t[5],t[4],t[2],t[1],t[0])
        return rtc_external_datetime
    
    def read_time(self):
        t = self.bus.readfrom_mem(int(self.address),int(self.start_reg),7)
        a = t[0]&0x7F  #second
        b = t[1]&0x7F  #minute
        c = t[2]&0x3F  #hour
        d = t[3]&0x07  #week
        e = t[4]&0x3F  #day
        f = t[5]&0x1F  #month
        #print("20%x/%02x/%02x %02x:%02x:%02x %s" %(t[6],t[5],t[4],t[2],t[1],t[0],self.w[t[3]-1]))
        rtc_external_time = "%02x:%02x:%02x" %(t[2],t[1],t[0])
        return rtc_external_time

    def set_alarm_time(self,alarm_time):
        #    init the alarm pin
        self.alarm_pin = Pin(ALARM_PIN,Pin.IN,Pin.PULL_UP)
        #    set alarm irq
        self.alarm_pin.irq(lambda pin: print("alarm1 time is up"), Pin.IRQ_FALLING)
        #    enable the alarm1 reg
        self.bus.writeto_mem(int(self.address),int(self.control_reg),b'\x05')
        #    convert to the BCD format
        hour = alarm_time[0] + alarm_time[1]
        minute = alarm_time[3] + alarm_time[4]
        second = alarm_time[6] + alarm_time[7]
        date = alarm_time.split(",",2)[2][8] + alarm_time.split(",",2)[2][9]
        now_time = binascii.unhexlify((second + " " + minute + " " + hour +  " " + date).replace(' ',''))
        #    write alarm time to alarm1 reg
        self.bus.writeto_mem(int(self.address),int(self.alarm1_reg),now_time)

def set_pico_rtc(year,month,day,weekday,hour,minutes,seconds,subseconds):
    rtc.datetime((year,month,day,weekday,hour,minutes,seconds,subseconds))
    return rtc.datetime()

def set_custom_date_dictionary(year, month, day, weekday):
    custom_date_dictionary['year'] = year
    custom_date_dictionary['month'] = month
    custom_date_dictionary['day'] = day
    custom_date_dictionary['weekday'] = weekday
    return custom_date_dictionary

def set_custom_time_dictionary(hour, minutes, seconds, subseconds):
    custom_time_dictionary['hour'] = hour
    custom_time_dictionary['min'] = minutes
    custom_time_dictionary['sec'] = seconds
    custom_time_dictionary['subsec'] = subseconds
    return custom_time_dictionary

# RP2040 Datasheet, A microcontroller by Raspberry Pi

# https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf?_gl=1*16bx0wt*_ga*NTgzOTA2NDMxLjE2ODg5MTAyNjI.*_ga_22FD70LWDS*MTY5Nzk2MzU1MC4yLjEuMTY5Nzk2MzU2NS4wLjAuMA..

# 4.9.5. Temperature Sensor

# The temperature sensor measures the Vbe voltage of a biased bipolar diode, connected to the fifth ADC channel
# (AINSEL=4). Typically, Vbe = 0.706V at 27 degrees C, with a slope of -1.721mV per degree. Therefore the temperature
# can be approximated as follows:

# T = 27 - (ADC_voltage - 0.706)/0.001721

# As the Vbe and the Vbe slope can vary over the temperature range, and from device to device, some user calibration
# may be required if accurate measurements are required.

def readTemperature(temperatureCalibration):
    adc_value = temperatureSensor.read_u16()
    ADC_voltage = (3.3/65535) * adc_value
    temperature = 27 - (ADC_voltage - 0.706) / 0.001721
    return temperature + temperatureCalibration

def centigradeToFahrenheit(centigrade):
    fahrenheit = centigrade * 9/5 + 32
    return fahrenheit

def circle(cx,cy,r,c): # Centre (x,y), radius, colour
    for angle in range(0, 90, 1): # 0 to 90 degrees in 1 step
        y3=int(r*math.sin(math.radians(angle))) # 4 quadrants
        x3=int(r*math.cos(math.radians(angle)))
        OLED128X32.pixel(cx-x3,cy+y3,c)
        OLED128X32.pixel(cx-x3,cy-y3,c)
        OLED128X32.pixel(cx+x3,cy+y3,c)
        OLED128X32.pixel(cx+x3,cy-y3,c)

def displayDegreesSymbolToOled(temperatureString, yPosition):
    temperatureStringLength = len(temperatureString)
        
    if temperatureStringLength == 7:
        circle(61,yPosition,2,1)
        
    if temperatureStringLength == 6:
        circle(53,yPosition,2,1)
        
    if temperatureStringLength == 5:
        circle(45,yPosition,2,1)
            
    if temperatureStringLength == 4:
        circle(37,yPosition,2,1)
            
def displayCalibrationToOled():
    
    calibrationAdjustment = 0
    buttonRed_Prev_State = False
    buttonGreen_Prev_State = False
    
    while buttonBlue.value() == 0:
        
        OLED128X32.fill(0)
        OLED128X32.text("Calibration  +/-", 0, 0)
    
        temperature = readTemperature(calibrationAdjustment)
        
        degreesC = "{:.2f}".format(temperature)
        degreesF = "{:.2f}".format(centigradeToFahrenheit(temperature))
        
        OLED128X32.text(str(degreesC) + chr(32) + "C", 0, 10)
        displayDegreesSymbolToOled(degreesC, oledLine2)
        print("Calibration: " + str(temperature) + "°C ")
        
        OLED128X32.text(str(degreesF) + chr(32) + "F", 0, 20)
        displayDegreesSymbolToOled(degreesF, oledLine3)
        print("Calibration: " + str(centigradeToFahrenheit(temperature)) + "°F ")
        OLED128X32.text(str(degreesF) + chr(32) + "F", 0, 20)
        
        OLED128X32.text(str(calibrationAdjustment) + chr(32), 88, 20)
        print("Calibration Adjustment: " + str(calibrationAdjustment) + "°C ")
        print("")
        
        timestring = str(rtc_external.read_time())
        OLED128X32.text(str(timestring), 88, 10)
        OLED128X32.show()
        
        if (buttonRed.value() and (buttonRed_Prev_State == False)):
            calibrationAdjustment = calibrationAdjustment - 1
            buttonRed_Prev_State = True
        elif (buttonRed.value() == False) and (buttonRed_Prev_State == True):
            buttonRed_Prev_State = False

        if (buttonGreen.value() and (buttonGreen_Prev_State == False)):
            calibrationAdjustment = calibrationAdjustment + 1
            buttonGreen_Prev_State = True
        elif (buttonGreen.value() == False) and (buttonGreen_Prev_State == True):
            buttonGreen_Prev_State = False
        
        time.sleep(.1)
    
    return calibrationAdjustment

def displayInformationToOled(index, temperature):
    OLED128X32.fill(0)
    OLED128X32.text("Temperature  " + str(interval) + "s", 0, 0)
    
    #temperature = -40.00
    #temperature = 150.00
    
    degreesC = "{:.2f}".format(temperature)
    degreesF = "{:.2f}".format(centigradeToFahrenheit(temperature))
    
    if unit_type == "C":
        OLED128X32.text(str(degreesC) + chr(32) + "C", 0, 10)
        print("Temperature: " + str(temperature) + "°C " + str(interval) + " seconds interval (" + datetimestring + ") Calibration Adjustment " + str(temperatureCalibration) + "°C")
        displayDegreesSymbolToOled(degreesC, oledLine2)
    else:
        OLED128X32.text(str(degreesF) + chr(32) + "F", 0, 10)
        print("Temperature: " + str(centigradeToFahrenheit(temperature)) + "°F "  + str(interval) + " seconds interval (" + datetimestring + ") Calibration Adjustment " + str(centigradeToFahrenheit(temperatureCalibration)) + "°F")
        displayDegreesSymbolToOled(degreesF, oledLine2)
        
    OLED128X32.text(str(timestring), 88, 10)

    if logging == False:
        if index > 1:
            print("Logged: " + str(index))
            OLED128X32.text("Logged: " + str(index), 0, 20)
    else:
        print("Logging: " + str(index))
        OLED128X32.text("Logging: " + str(index), 0, 20)
        index = index + 1

    if displayOnOff == True:
        OLED128X32.fill(0)
             
    OLED128X32.show()
    
    return index

def logDataToCsvFile(csvFieldNamesWritten, temperature):
    if logging:
        loggingLed.value(1)
        if csvFieldNamesWritten:
            file=open("temperature" + filename + no_battery_rtc_filename_suffix + ".csv","a") # Append and opening of a CSV file in Write mode
        else:
            file=open("temperature" + filename + no_battery_rtc_filename_suffix + ".csv","w") # Append and opening of a CSV file in Write mode
            file.write("temperature,unit,calibration_adjustment,interval_seconds,datetime" + chr(10)) # Writing data in the opened file
            csvFieldNamesWritten = True
            
        if unit_type == "C":
            file.write(str(temperature) + ",centigrade," + str(temperatureCalibration) + "," + str(interval) + "," + datetimestring + chr(10))
        else:
            file.write(str(centigradeToFahrenheit(temperature)) + ",fahrenheit,"  + str(centigradeToFahrenheit(temperatureCalibration)) + "," + str(interval) + "," + datetimestring + chr(10))
    
        file.close()
        time.sleep(0.5)
        loggingLed.value(0)
        
        return csvFieldNamesWritten

rtc=machine.RTC()
rtc_external=ds3231(RTC_EXTERNAL_I2C0_PORT,RTC_EXTERNAL_I2C0_SCL,RTC_EXTERNAL_I2C0_SDA)

#datetimestamp = rtc.datetime()
#datetimestring = "%04d-%02d-%02d %02d:%02d:%02d"%(datetimestamp[0:3] + datetimestamp[4:7])
#datestring = "%04d-%02d-%02d"%(datetimestamp[0:3])
#timestring = "%02d:%02d:%02d"%(datetimestamp[4:7])

datetimestamp = str(rtc_external.read_datetime())
datetimestring = datetimestamp
timestring = str(rtc_external.read_time())

utc = datetimestring.replace(":", "")
filename = utc.replace(" ", "_")
randomstring = str(random.random())
#no_battery_rtc_filename_suffix = "_" + randomstring.replace(".", "")
no_battery_rtc_filename_suffix = ""

#print("datestring, timestring: " + datestring, timestring)
#print("custom_date_dictionary: " + str(set_custom_date_dictionary(datetimestamp[0],datetimestamp[1],datetimestamp[2],datetimestamp[3])))
#print("custom_time_dictionary: " + str(set_custom_time_dictionary(datetimestamp[4],datetimestamp[5],datetimestamp[6],datetimestamp[7])))
#print("rtc.datetime(): " + str(set_pico_rtc(custom_date_dictionary['year'], custom_date_dictionary['month'], custom_date_dictionary['day'], custom_date_dictionary['weekday'], custom_time_dictionary['hour'], custom_time_dictionary['min'], custom_time_dictionary['sec'], custom_time_dictionary['subsec'])))

OLED128X32.fill(0)
OLED128X32.blit(splashScreen, 0, 0)
OLED128X32.show()
time.sleep(5)

temperatureCalibration = displayCalibrationToOled()

while buttonBlue.value() == 1:
    displayOnOff = False

while True:
    Potentiometer = adcPotentiometer.read_u16()
    # print (duty)
    
    if Potentiometer > 0 and Potentiometer < 20000:
        interval = 15
        
    if Potentiometer > 20000 and Potentiometer < 40000:
        interval = 30
        
    if Potentiometer > 40000 and Potentiometer < 65535:
        interval = 60
        
    #datetimestamp = rtc.datetime()
    #datetimestring = "%04d-%02d-%02d %02d:%02d:%02d"%(datetimestamp[0:3] + datetimestamp[4:7])
    #datestring = "%04d-%02d-%02d"%(datetimestamp[0:3])
    #timestring = "%02d:%02d:%02d"%(datetimestamp[4:7])

    datetimestamp = str(rtc_external.read_datetime())
    datetimestring = datetimestamp
    timestring = str(rtc_external.read_time())

    temperatureCurrent = readTemperature(temperatureCalibration)
    
    index = displayInformationToOled(index, temperatureCurrent)       
    csvFieldNamesWritten = logDataToCsvFile(csvFieldNamesWritten, temperatureCurrent)
        
    timer = 0
    while timer < interval:
        timer = timer + 1

        if buttonGreen.value():
            displayOnOff = False
            onboardled.off()
                
            if unit_type == "C":
                unit_type = "F"       
            else:
                unit_type = "C"
            
            index = displayInformationToOled(index, temperatureCurrent)
        
        if buttonRed.value():
            displayOnOff = False
            onboardLed.off()
            
            if logging:
                logging = False
            else:
                logging = True
                
            index = displayInformationToOled(index, temperatureCurrent)
                
        if buttonBlue.value():
            if displayOnOff:            
                displayOnOff = False
                onboardLed.off()
                index = displayInformationToOled(index, temperatureCurrent)
            else:
                displayOnOff = True
                OLED128X32.fill(0)         
                OLED128X32.show()
                onboardLed.on()
                 
        time.sleep(1)
        #sys.exit()
        
