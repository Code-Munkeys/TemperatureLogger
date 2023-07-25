# Designed and Developed by Franz Ayestaran - http://franz.ayestaran.co.uk

# You may use this code in your own projects and upon doing so, you the programmer are solely
# responsible for determining it's worthiness for any given application or task. Here clearly
# states that the code is for learning purposes only and is not guaranteed to conform to any
# programming style, standard, or be an adequate answer for any given problem.

# Raspberry Pi Pico with external RTC

# Usage:
#
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
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, ADC

adcpin = 4
sensor = machine.ADC(adcpin)

adc = ADC(Pin(26))

led = Pin(15, Pin.OUT)

w = 128
h = 32
unit_type = "C"

OLED_I2C1 = I2C(1, scl=Pin(3), sda=Pin(2), freq=200000)
OLED_I2C1_ADDR = OLED_I2C1.scan()[0]
OLED128X32 = SSD1306_I2C(w, h, OLED_I2C1, OLED_I2C1_ADDR)
print("OLED_I2C1 Addr: " + str(OLED_I2C1_ADDR))

buttonBlue = Pin(6, Pin.IN, Pin.PULL_DOWN)
buttonRed = Pin(14, Pin.IN, Pin.PULL_DOWN)
buttonGreen = Pin(10, Pin.IN, Pin.PULL_DOWN)

RTC_EXTERNAL_I2C0_PORT = 0
RTC_EXTERNAL_I2C0_SDA = 20
RTC_EXTERNAL_I2C0_SCL = 21
RTC_EXTERNAL_I2C0_ALARM_PIN = 3

logging = False
index = 1
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

def readTemperature():
    adc_value = sensor.read_u16()
    volt = (3.3/65535)*adc_value
    temperature = 27 - (volt - 0.706)/0.001721
    return temperature

def centigradeToFahrenheit(centigrade):
    fahrenheit = centigrade * 9/5 + 32
    return fahrenheit

def displayInformationToOled(index):
    OLED128X32.fill(0)
    OLED128X32.text("Temperature  " + str(interval) + "s", 0, 0)
    
    if unit_type == "C":
        OLED128X32.text(str(round(temperature,2)) + " " + chr(42) + "C", 0, 10)
        print("Temperature: " + str(temperature) + "°C " + str(interval) + " seconds interval (" + datetimestring + ")")  
    else:
        OLED128X32.text(str(round(centigradeToFahrenheit(temperature),2)) + " " + chr(42) + "F", 0, 10)
        print("Temperature: " + str(centigradeToFahrenheit(temperature)) + "°F "  + str(interval) + " seconds interval (" + datetimestring + ")")
        
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

def logDataToCsvFile(csvFieldNamesWritten):
    if logging:
        led.value(1)
        if csvFieldNamesWritten:
            file=open("temperature" + filename + no_battery_rtc_filename_suffix + ".csv","a") # Append and opening of a CSV file in Write mode
        else:
            file=open("temperature" + filename + no_battery_rtc_filename_suffix + ".csv","w") # Append and opening of a CSV file in Write mode
            file.write("temperature,unit,interval_seconds,datetime" + chr(10)) # Writing data in the opened file
            csvFieldNamesWritten = True
            
        if unit_type == "C":
            file.write(str(temperature) + ",centigrade," + str(interval) + "," + datetimestring + chr(10))
        else:
            file.write(str(centigradeToFahrenheit(temperature)) + ",fahrenheit," + str(interval) + "," + datetimestring + chr(10))
    
        file.close()
        time.sleep(0.5)
        led.value(0)
        
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

onboardled = Pin("LED", Pin.OUT)
onboardled.off()

while True:
    duty = adc.read_u16()
    # print (duty)
    
    if duty > 0 and duty < 20000:
        interval = 15
        
    if duty > 20000 and duty < 40000:
        interval = 30
        
    if duty > 40000 and duty < 65535:
        interval = 60
        
    #datetimestamp = rtc.datetime()
    #datetimestring = "%04d-%02d-%02d %02d:%02d:%02d"%(datetimestamp[0:3] + datetimestamp[4:7])
    #datestring = "%04d-%02d-%02d"%(datetimestamp[0:3])
    #timestring = "%02d:%02d:%02d"%(datetimestamp[4:7])

    datetimestamp = str(rtc_external.read_datetime())
    datetimestring = datetimestamp
    timestring = str(rtc_external.read_time())

    temperature = readTemperature()
    
    index = displayInformationToOled(index)       
    csvFieldNamesWritten = logDataToCsvFile(csvFieldNamesWritten)
        
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
            
            index = displayInformationToOled(index)
        
        if buttonRed.value():
            displayOnOff = False
            onboardled.off()
            
            if logging:
                logging = False
            else:
                logging = True
                
            index = displayInformationToOled(index)
                
        if buttonBlue.value():
            if displayOnOff:            
                displayOnOff = False
                onboardled.off()
                index = displayInformationToOled(index)
            else:
                displayOnOff = True
                OLED128X32.fill(0)         
                OLED128X32.show()
                onboardled.on()
                 
        time.sleep(1)
        