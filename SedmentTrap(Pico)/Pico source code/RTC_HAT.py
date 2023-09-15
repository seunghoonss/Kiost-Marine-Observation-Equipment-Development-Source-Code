#!/usr/bin/python
# -*- coding: utf-8 -*-
from machine import I2C
import time

address = 0x68
register = 0x00
#sec min hour week day month year
CurrentTime = b'\x30\x05\x16\x05\x22\x09\x22' #00:00:01 friday 16/04/2021 
week  = ["Sun","Mon","Tues","Wed","Thur","Fri","Sat"];

bus = I2C(1) # i2c 1

def PicoRTCSetTime():
	bus.writeto_mem(int(address),int(register),CurrentTime)

def PicoRTCReadTime():
	return bus.readfrom_mem(int(address),int(register),7);

PicoRTCSetTime() #You can remove this line once time is set
while 1:
	data = PicoRTCReadTime()
	a = data[0]&0x7F  #sec
	b = data[1]&0x7F  #min
	c = data[2]&0x3F  #hour
	d = data[3]&0x07  #week
	e = data[4]&0x3F  #day
	f = data[5]&0x1F  #month
	g = data[6]&0x3F #year
	print("20%x/%02x/%02x %02x:%02x:%02x %s" %(g,f,e,c,b,a,week[d-1])) #year,month,day,hour,min,sec,week
	time.sleep(1)


