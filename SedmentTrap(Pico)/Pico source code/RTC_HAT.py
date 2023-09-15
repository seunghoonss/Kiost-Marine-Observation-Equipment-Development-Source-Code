#!/usr/bin/python
# -*- coding: utf-8 -*-
from machine import I2C
import utime
import binascii
bus = I2C(1) # i2c 1

address = 0x68
register = 0x00
def PicoRTCSetTime():
	bus.writeto_mem(int(address),int(register),CurrentTime)

def PicoRTCReadTime():
	return bus.readfrom_mem(int(address),int(register),7);

#sec min hour week day month year
time1 = utime.localtime()
#print(time1)

#time1 = PicoRTCReadTime()
a = time1[0]  #sec
b = time1[1]  #min
c = time1[2] #hour
d = time1[3]  #week
e = time1[4]  #day
f = time1[5]  #month
g = time1[6] #year
#timerefine(potime,potime1) # potime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
#print(str(potime1[0])+" "+str(potime1[1])+" "+str(potime1[2])+" "+str(potime1[3])+" "+str(potime1[4])+" "+str(potime1[5])+" "+str(potime1[6]))
year = str(hex(g%100))
month = str(hex(f))
day = str(hex(e))
weekday = str(hex(d))
hour = str(hex(c))
minute = str(hex(b))
second = str(hex(a))
print(year+" "+month+" "+day+" "+hour+" "+minute+" "+second)
CurrentTime_value=year+" "+month+" "+day+" "+hour+" "+minute+" "+second
CurrentTime= binascii.unhexlify(CurrentTime_value.replace(' ', ''))
#CurrentTime = bytes('\.'+second+minute+hour+weekday+day+month+year,"utf-8")
#print(CurrentTime)
#CurrentTime = b'\x00\x00\x01\x06\x16\x04\x21' #00:00:01 friday 16/04/2021
week  = ["Sun","Mon","Tues","Wed","Thur","Fri","Sat"];


PicoRTCSetTime()
#PicoRTCSetTime() #You can remove this line once time is set
while 1:
	#PicoRTCSetTime()
	data = PicoRTCReadTime()
	print(data)
	
	a = data[0]&0x7F  #sec
	b = data[1]&0x7F  #min
	c = data[2]&0x3F  #hour
	d = data[3]&0x07  #week
	e = data[4]&0x3F  #day
	f = data[5]&0x1F  #month
	g = data[6]&0x3F #year
	
	print("20%x/%02x/%02x %02x:%02x:%02x %s" %(g,f,e,c,b,a,week[d-1])) #year,month,day,hour,min,sec,week
	utime.sleep(1)
