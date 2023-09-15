import picosleep
import time
from machine import Pin
from time import sleep
import machine
#import datetime

led = Pin(25, Pin.OUT)


#Set Time
min_val = 1
hour_val = 3
day_val = 3


min_to_sec = min_val * 60
hour_to_sec = hour_val * 60 * 60
day_to_sec = day_val * 60 * 60 * 24

current_time = time.time()

future_min_time = current_time + min_to_sec
#future_hour_time = current_time + hour_to_sec
#future_day_time = current_time + day_to_sec

formatted_future_time = time.localtime(future_min_time)
print("Wake up 예정시간:")
print(str(formatted_future_time[0])+"-"+str(formatted_future_time[1])+"-"+str(formatted_future_time[2])+"  "+str(formatted_future_time[3])+":"+str(formatted_future_time[4])+":"+str(formatted_future_time[5]))

startflag = 1
while (startflag) :
    
    led.toggle()
    time.sleep(10)
    led.toggle()
    print("picosleep start")
    
    
      
    picosleep.seconds(min_to_sec)
    #picosleep.seconds(hour_to_sec)
    #picosleep.seconds(day_to_sec)
    
    #print("---------------------------------")
    while(1):
        led.toggle()
        time.sleep(0.5)
        
    #print("picosleep end")
   
    startflag = 0
