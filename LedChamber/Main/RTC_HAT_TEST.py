#!/usr/bin/python
# -*- coding: utf-8 -*-
from machine import I2C
import time
import binascii

address = 0x68
register = 0x00
#sec min hour week day month year
week  = ["Sun","Mon","Tues","Wed","Thur","Fri","Sat"];
bus = I2C(1) # i2c 1

class RTC_HAT:
    def __init__(self, year, mon, day, weekday, hour, minute, sec):
        self.year = year
        self.mon = mon
        self.day = day
        self.weekday = weekday
        self.hour = hour
        self.minute = minute
        self.sec = sec
        self.CurrentTime = CurrentTime
        
#+'\x'+str(minute)+'\x'+str(hour)+'\x'+str(weekday)+'\x'+str(day)+'\x'+str(mon)+'\x'+str(year)
    def CurrentTimeSet(year, month, day, weekday, hour, minute, second):
        global CurrentTime
        CurrentTime_value = second+" "+minute+" "+hour+" "+weekday+" "+day+" "+month+" "+year
        CurrentTime = binascii.unhexlify(CurrentTime_value.replace(' ', ''))
        
    def PicoRTCSetTime():
        bus.writeto_mem(int(address),int(register),CurrentTime)

    def PicoRTCReadTime():
        return bus.readfrom_mem(int(address),int(register),7);




# 
# b'\x30\x05\x16\x05\x22\x09\x22'


