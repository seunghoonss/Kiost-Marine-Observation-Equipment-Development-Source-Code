from machine import UART, Pin, PWM , I2C, RTC
import time
from ds3231_i2c import DS3231_I2C
from io import StringIO
import os
from RTC_HAT_TEST import RTC_HAT
import binascii
import picosleep

led = Pin(25, Pin.OUT)

def return_print(*message):
    io = StringIO()
    print(*message, file=io, end="")
    return io.getvalue()

def timerefine(variable_a,variable_b) :
    for i in range(len(variable_a)) :
        variable_b[i] = int(return_print("%02x"%variable_a[i]))
    variable_b.reverse()
    variable_b.append(0)
    variable_b[0] = variable_b[0]+2000
    
    return variable_a,variable_b

ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
rtc = DS3231_I2C(ds_i2c)

potime = rtc.read_time()                                
potime1 = [0 for i in range(len(potime))]
timerefine(potime,potime1)
print(str(potime1[0])+" "+str(potime1[1])+" "+str(potime1[2])+" "+str(potime1[4])+" "+str(potime1[5])+" "+str(potime1[6]))
#Set Time
min_val = 1
hour_val = 15
day_val = 30


min_to_sec = min_val * 60
hour_to_sec = hour_val * 60 * 60
day_to_sec = day_val * 60 * 60 * 24

current_time = time.time()

future_min_time = current_time + min_to_sec
future_hour_time = current_time + hour_to_sec
future_day_time = current_time + day_to_sec

#formatted_future_time = time.localtime(future_min_time)
formatted_future_time = time.localtime(future_hour_time)
#formatted_future_time = time.localtime(future_day_time)

print("Wake up 예정시간:")
print(str(formatted_future_time[0])+"-"+str(formatted_future_time[1])+"-"+str(formatted_future_time[2])+"  "+str(formatted_future_time[3])+":"+str(formatted_future_time[4])+":"+str(formatted_future_time[5]))



timecount = hour_to_sec // 3600
left_sec = hour_to_sec % 3600 

#timecount = min_to_sec // 604800 
#left_sec = min_to_sec % 604800  
"""
timecount = day_to_sec // 604800 #일주일을 몇번 잠들게 할 건지
left_sec = day_to_sec % 604800  #일주일 이내의 남은 시간(초)
"""

print("timecount="+str(timecount))
print("left_sec="+str(left_sec))
startflag = 1
while (startflag) :
    
    #picosleep중일 떄는 print금지
    
    #thonny연결 하려고 10초
    led.toggle()
    time.sleep(10)
    led.toggle()
    print("picosleep start")
    potime = rtc.read_time()                                
    potime1 = [0 for i in range(len(potime))]
    timerefine(potime,potime1)
    #print(str(potime1[0])+" "+str(potime1[1])+" "+str(potime1[2])+" "+str(potime1[4])+" "+str(potime1[5])+" "+str(potime1[6]))
    
    f = open("picosleep_log"+str(potime1[0])+str(potime1[1])+str(potime1[2])+str(potime1[4])+str(potime1[5])+str(potime1[6]),"w")
    f.write("[picosleep start]"+ str(potime1[0])+"/"+str(potime1[1])+"/"+str(potime1[2])+"/"+"  "+str(potime1[4])+":"+str(potime1[5])+":"+str(potime1[6])+"\r\n")
    f.close()
    #min_to_sec % 일주일 초 = 일주일 이내의 남은 시간 = left_sec
    #min_to_sec / 일주일 초 = 일주일을 몇번 잠들게 할 건지 = timecount
    
    for a in range (timecount):
        time.sleep(0.1)
        picosleep.seconds(3600) #일주일을 초= 604800초
        
        Fpotime = rtc.read_time()                                
        Fpotime1 = [0 for i in range(len(potime))]
        timerefine(Fpotime,Fpotime1)
        f = open("picosleep_log"+str(potime1[0])+str(potime1[1])+str(potime1[2])+str(potime1[4])+str(potime1[5])+str(potime1[6]),"a")
        f.write("[pico wake]"+ str(Fpotime1[0])+"/"+str(Fpotime1[1])+"/"+str(Fpotime1[2])+"/"+"  "+str(Fpotime1[4])+":"+str(Fpotime1[5])+":"+str(Fpotime1[6])+"\r\n")
        f.close()
        
        led.toggle()
        #기록@@@@@@@@@@@@@@@@@@@@@@@@@@@
    
    #picosleep 0초는 프로그램 멈춤
    if left_sec == 0:
        pass
    else:
        time.sleep(0.1)
        picosleep.seconds(left_sec)
        
    
    #기록@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    Fpotime = rtc.read_time()                                
    Fpotime1 = [0 for i in range(len(potime))]
    timerefine(Fpotime,Fpotime1)
    f = open("picosleep_log"+str(potime1[0])+str(potime1[1])+str(potime1[2])+str(potime1[4])+str(potime1[5])+str(potime1[6]),"a")
    f.write("[pico last wake]"+ str(Fpotime1[0])+"/"+str(Fpotime1[1])+"/"+str(Fpotime1[2])+"/"+"  "+str(Fpotime1[4])+":"+str(Fpotime1[5])+":"+str(Fpotime1[6])+"\r\n")
    f.close()

    
    
    
    #picosleep.seconds(min_to_sec)
    #picosleep.seconds(hour_to_sec)
    #picosleep.seconds(day_to_sec)
    

    #깨어나면
    while(1):
        led.toggle()
        time.sleep(0.5)
        
    startflag = 0

