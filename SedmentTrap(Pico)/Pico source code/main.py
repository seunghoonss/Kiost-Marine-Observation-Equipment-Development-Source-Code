#Pyboard v1.0 
from ds3231_i2c import DS3231_I2C
import machine
from machine import RTC , I2C, Pin , PWM ,SPI
#from pyb import Pin, Timer
from utime import sleep, time
import utime as time
from io import StringIO
from mpu9250 import MPU9250
import picosleep
import sdcard , os

#motor driver run define set
def RotateCW(pwm):
    pwma.duty_u16(int((pwm*0.01)*65535))
    ina1.value(1)
    ina2.value(0)

def RotateCCW(pwm):
    pwma.duty_u16(int((pwm*0.01)*65535))
    ina1.value(0)
    ina2.value(1)

def StopMotor():

    ina1.value(0)
    ina2.value(0)
#     pwma.duty_u16(0)
    #ch.pulse_width_percent(0)
    pwma.duty_u16(int((0*0.01)*65535))

def CWStopMotor(duty):
    ina1.value(0)
    ina2.value(1)
#     pwma.duty_u16(10)
    time.sleep(1)

def CCWStopMotor(duty):
    ina1.value(1)
    ina2.value(0)
#     pwma.duty_u16(10)
    time.sleep(1)

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
led = Pin(25, Pin.OUT)

"""
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
sd = sdcard.SDCard(spi, Pin(13))
vfs = os.VfsFat(sd)

os.mount(sd, '/sd')
"""
while True:
    try:
        spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
        sd = sdcard.SDCard(spi, Pin(13))
        vfs = os.VfsFat(sd)

        os.mount(sd, '/sd')
        
        #files = os.listdir('/sd')
        # Process files on the SD card
        #for file in files:
            # Do something with the file
            #print(file)
        break
    except OSError:
        # SD card not available, retry after a short delay
        time.sleep(1)
        print("Sleep")
        continue

#motor driver pin set A motor
ina1 = Pin(14,Pin.OUT)#motor
ina2 = Pin(15,Pin.OUT)  
pwma = PWM(Pin(26))
pwma.freq(1000)

#Hall sensor

hs=Pin(22,Pin.IN)



path = "/sd"
file_list = os.listdir(path)

print ("file_list: {}".format(file_list))


# gui start
gui_flag = 1
gui_count = 0
gui_list = []
gui_position_x = 0
gui_position_y = 0
gui_position_z = 0

#Gyro Sensor Setting
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
sensor = MPU9250(i2c)

ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
rtc = DS3231_I2C(ds_i2c)

uart1 = machine.UART(1, baudrate = 19200 , tx = Pin(8), rx = Pin(9)) #Oxyzen Sensor UART
gui_led = Pin(25, Pin.OUT)
                    

while(gui_flag):
    try:
        while True:
            gui_count += 1
            led.toggle()
            
            print(gui_count)
            if gui_count == 30:
                
                gui_flag = 0
                break           
            rxData = uart1.read()
            if not rxData == None:              
                data = rxData.decode('utf-8')
                if data == "start":
                    uart1.write("CONNECT_SUCCESS")
                    time.sleep(0.1)
                                        
                    while True:
                        try:
                            rxData = uart1.read()
                            data = rxData.decode('utf-8')
                            time.sleep(0.5)
                            
                            if data == "start":
                                uart1.write("CONNECT_SUCCESS")
                                

                            if data == "delete_file":
             
                                rxData = uart1.read()
                                data=rxData.decode('utf-8')
                                
                                
                                if "txt" in data:
                                    file_path="/sd/"+data
                                    #print(file_path)
                                    os.remove(file_path)
                                    print("file removed")
                                else:
                                    print("failed delete")

                            
                            if data == "config_save":
                                #print("^_^")
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                print(data)
                                
                                f = open("config.cfg","w")
                                f.write(data)
                                f.close()
                                
                                
                                f = open("config.cfg", 'r')
                                line = f.readlines()
                                for line in line:
                                    item = line.split(" ")
                                    delaytimeminute = item[item.index("startdelaytimeminute")+1]
                                    timecycleindex = item[item.index("on")+1]
                                    timecyclevalue = item[item.index("on")+2]
                                    cwpwmvalue = item[item.index("CW")+1]
                                    ccwpwmvalue = item[item.index("CCW")+1]
                                f.close()
                                #print(delaytimeminute+"~"+timecycleindex+"~"+timecyclevalue+"~"+cwpwmvalue+"~"+ccwpwmvalue)
                        
                                
                            if data == "data_name":
                                
                                file_list = os.listdir('/sd')
                                for i in range(len(file_list)):
                                    uart1.write(str(file_list[i]))
                                    time.sleep(0.5)
                                    uart1.write(" ")

                                
                            if data == "data_transfer":
                                
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                
                                file_name = "/sd/"+ data
                                loggingfileMatrix = []
                                

                                with open(file_name) as file :
                                    for lineContent in file: # Point.1
                                        loggingfileMatrix.append(lineContent.strip('\n'))
                        
                                for i in range(len(loggingfileMatrix)):
                                    uart1.write(str(loggingfileMatrix[i]))
                                    time.sleep(0.1)
                                    uart1.write("\n")
                                    time.sleep(0.02)
                                
                                
                                uart1.write("\n")
                                uart1.write("END")
                                
                                gui_led.toggle()
                                
                            if data == "GyroCheck":
                                """
                                for a in range(10):
                                    print("!")
                                    acc_list = sensor.acceleration
                                    gui_position_x = gui_position_x+acc_list[0]
                                    gui_position_y = gui_position_y+acc_list[1]
                                    gui_position_z = gui_position_z+acc_list[2]
                                    sleep(1)
                                gui_position_x = gui_position_x/10
                                gui_position_y = gui_position_y/10
                                gui_position_z = gui_position_z/10
                                """
                                acc_list = sensor.acceleration
                                #print("delay time start Position value : x = "+str(round(acc_list[0],3))+", y = "+str(round(acc_list[1],3))+", z ="+str(round(acc_list[2],3)))
                                datauart=str(round(acc_list[0],3))+" "+str(round(acc_list[1],3))+" "+str(round(acc_list[2],3))
                                uart1.write(datauart)
                                #x,y,z 값 pc로 전송
                        
                                gui_position_x=0
                                gui_position_y=0
                                gui_position_z=0
                            
                            if data == "sim_control":
                                p = uart1.read().decode('utf-8')
                                p_2 = p.split()
                                #print(p_2[0]+" ~ "+ p_2[1])
                                motorrun = 1
                                while(motorrun):
                                    RotateCW(int(p_2[0]))
                                    sleep(0.8)
                                    circlecheck =  1
                                    while(circlecheck):
                                        if hs.value() == 0:
                                            RotateCCW(int(p_2[1]))
                                            sleep(0.1)
                                            StopMotor()
                                            sleep(0.1)
                                            motorrun = 0
                                            circlecheck=0
                                
                            
                            if data == "CW_control":
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                
                                time.sleep(0.05)
                                
                                RotateCW(int(data))
                                """
                                circlecheck =  1
                                while(circlecheck):
                                    
                                    
                                    #rxData = uart1.read()
                                    #data = rxData.decode('utf-8')
                                    #time.sleep(0.05)
                                    #if data == "CW_Stop":
                                        #StopMotor()
                                        #circlecheck=0
                                
                                    if hs.value() == 0:
                                        RotateCCW(10)
                                        sleep(0.1)
                                        StopMotor()
                                        sleep(0.1)
                                        circlecheck=0"""
                                    
                            
                            if data == "CW_Stop":                        
                                StopMotor()
                            
                            if data == "CCW_control":
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                
                                time.sleep(0.05)
                                
                                RotateCCW(int(data))
                                """circlecheck =  1
                                while(circlecheck):
                                    if hs.value() == 0:
                                        RotateCW(10)
                                        sleep(0.1)
                                        StopMotor()
                                        sleep(0.1)
                                        circlecheck=0"""
                            
                            if data == "CCW_Stop":                        
                                StopMotor()
                                
                    
                            if data == "time_check":
                                
                                #ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
                                #rtc = DS3231_I2C(ds_i2c)

                                potime = rtc.read_time()                                
                                potime1 = [0 for i in range(len(potime))]
                                timerefine(potime,potime1) # potime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
                                
                                uart1.write(str(potime1[0])+" "+str(potime1[1])+" "+str(potime1[2])+" "+str(potime1[3])+" "+str(potime1[4])+" "+str(potime1[5])+" "+str(potime1[6]))
                                uart1.write("\n")
                                
                                time.sleep(0.1)
                                                            
                            if data == "time_save":        
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                time_Data = data.split()
                                year = time_Data[0]
                                month = time_Data[1]
                                day = time_Data[2]
                                weekday = time_Data[3]
                                hour = time_Data[4]
                                minute = time_Data[5]
                                second = time_Data[6]
                                
                                RTC_HAT.CurrentTimeSet(year, month, day, weekday, hour, minute, second)
                                RTC_HAT.PicoRTCSetTime()
                             
                                time.sleep(0.1)
                        
                        except Exception as e :
                            continue
                        
#                     gui_led.toggle()
               

            time.sleep(1)
        
    except Exception as e :
        continue


# program config - setting cycle time file open
timecyclehourindex = 0
timecycledayindex = 0
timecycleminuteindex = 0
sleepcount = 0

#cwpwmvalue=0
#ccwpwmvalue=0

f = open("config.cfg", 'r')
line = f.readlines()
for line in line:
    item = line.split(" ")
    delaytimeminute = item[item.index("startdelaytimeminute")+1]
    timecycleindex = item[item.index("on")+1]
    timecyclevalue = item[item.index("on")+2]
    cwpwmvalue = item[item.index("CW")+1]
    ccwpwmvalue = item[item.index("CCW")+1]
f.close()

timecyclevalue = int(timecyclevalue)
cwpwmvalue = int(cwpwmvalue)
ccwpwmvalue = int(ccwpwmvalue)

if str(timecycleindex) == 'timecycleminute':
    timecycleminute = timecyclevalue
    timecycleminuteindex = 1
if str(timecycleindex) == 'timecyclehour':
    timecyclehour = timecyclevalue
    timecyclehourindex = 1
if str(timecycleindex) == 'timecycleday':
    timecycleday = timecyclevalue
    timecycledayindex = 1
    
# sleepcalcurating
total_sleep = 0
seconds_checking = 0
operation_seconds = 0

startflag = 1
positiontime = 10
position_x = 0
position_y = 0
position_z = 0

if str(timecycleindex) == 'timecycleminute':
    seconds_checking = 60 * 1
if str(timecycleindex) == 'timecyclehour':
    seconds_checking = 60 * 60 * 1
if str(timecycleindex) == 'timecycleday':
    seconds_checking = 60 * 60 * 24 * 1

operation_seconds = int(timecyclevalue * seconds_checking)
delaytimeminute = int(delaytimeminute)

total_sleep = operation_seconds
delay_sleeptime = 0
delay_sleeptime = delaytimeminute * 60

#working cyclecount
cyclecount = 12

#delaytime and timecyclehour[string] convert integer
#trapwaittime = delaytimeminute
trapwaittime = int(delaytimeminute)

#trapcycletime check hour day month
if timecycleminuteindex == 1:
    trapcycletimeminute = int(timecycleminute)
    
if timecyclehourindex == 1:
    trapcycletimehour = int(timecyclehour)
    
if timecycledayindex == 1:    
    trapcycletimeday = int(timecycleday)

# Set DS I2C ID, SDA, SCL respective pins and uses default frequency (freq=400000)




# save timedata file 
#sttime = rtc.datetime()
potime = rtc.read_time()                                
potime1 = [0 for i in range(len(potime))]
timerefine(potime,potime1)


f = open("/sd/timedata" + ("%s%s%s%s%s%s" %(potime1[0],potime1[1],potime1[2],potime1[4],potime1[5],potime1[6])) + ".txt", "w" ,encoding='UTF-8')
f.close()
f = open("/sd/timedata" + ("%s%s%s%s%s%s" %(potime1[0],potime1[1],potime1[2],potime1[4],potime1[5],potime1[6])) + ".txt", "a" ,encoding='UTF-8')
f.write("KIO Sediment Trap V1 \n")
f.write("Start delay time : ")
f.write(str(delaytimeminute) +" minute \n")
f.write("trapcycletime : ")
if timecycleminuteindex == 1:
    trapcycletimeminute = int(timecycleminute)
    f.write(str(trapcycletimeminute) +" minute \n")
if timecyclehourindex == 1:
    trapcycletimehour = int(timecyclehour)
    f.write(str(trapcycletimehour) +" hour \n")
if timecycledayindex == 1:    
    trapcycletimeday = int(timecycleday)
    f.write(str(trapcycletimeday) +" day \n")
f.write("POWER ON Date Time : %s/%s/%s %s:%s:%s \n" %(potime1[0],potime1[1],potime1[2],potime1[4],potime1[5],potime1[6]))

for a in range(positiontime) :
    acc_list = sensor.acceleration
    position_x = position_x+acc_list[0]
    position_y = position_y+acc_list[1]
    position_z = position_z+acc_list[2]
    sleep(1)
        
position_x = position_x/positiontime # -124/10
position_y = position_y/positiontime # -10/10
position_z = position_z/positiontime # -290/10
                
f.write("delay time start Position value : x = "+str(round(position_x,3))+", y = "+str(round(position_y,3))+", z ="+str(round(position_z,3)))
f.write("\n")
f.close()

position_x = 0
position_y = 0
position_z = 0


# main program run
while startflag:
    starttimeflag = 1 
    while(starttimeflag):        
#         sleep(5)
        f = open("/sd/timedata" + ("%s%s%s%s%s%s" %(potime1[0],potime1[1],potime1[2],potime1[4],potime1[5],potime1[6])) + ".txt", "a" ,encoding='UTF-8')
        #t = rtc.datetime()
        t = rtc.read_time()                                
        t1 = [0 for i in range(len(potime))]
        timerefine(t,t1)
        
        f.write("--------------------------------------------------------------- \n")
        f.write("delay time start : %s/%s/%s %s:%s:%s \n" %(t1[0],t1[1],t1[2],t1[4],t1[5],t1[6]))
        sleep(0.5)
        picosleep.seconds(int(delay_sleeptime))
        #t = rtc.datetime()
        t = rtc.read_time()                                
        t1 = [0 for i in range(len(potime))]
        timerefine(t,t1)
        f.write("delay time end : %s/%s/%s %s:%s:%s \n" %(t1[0],t1[1],t1[2],t1[4],t1[5],t1[6]))
        f.write("--------------------------------------------------------------- \n")
        f.close()
        starttimeflag = 0
        motorrun = 1
        while(motorrun):
            RotateCW(cwpwmvalue)
            sleep(0.8)
            circlecheck =  1
            while(circlecheck):
                if hs.value() == 0:
                    RotateCCW(ccwpwmvalue)
                    sleep(0.1)
                    StopMotor()
                    sleep(0.1)
                    motorrun = 0
                    circlecheck=0
    for i in range(cyclecount):
        for a in range(positiontime) :
            acc_list = sensor.acceleration
            position_x = position_x+acc_list[0]
            position_y = position_y+acc_list[1]
            position_z = position_z+acc_list[2]
            sleep(1)
        
        position_x = position_x/positiontime # -124/10
        position_y = position_y/positiontime # -10/10
        position_z = position_z/positiontime # -290/10
        f = open("/sd/timedata" + ("%s%s%s%s%s%s" %(potime1[0],potime1[1],potime1[2],potime1[4],potime1[5],potime1[6])) + ".txt", "a" ,encoding='UTF-8')    
        f.write("cycle "+str(i+1)+" Position value : x = "+str(round(position_x,3))+", y = "+str(round(position_y,3))+", z ="+str(round(position_z,3)))
        f.write("\n")
        position_x = 0
        position_y = 0
        position_z = 0
        #t = rtc.datetime()
        t = rtc.read_time()                                
        t1 = [0 for i in range(len(potime))]
        timerefine(t,t1)
        #f.write("--------------------------------------------------------------- \n")
        f.write(str(i+1) + " ")
        f.write("bottle start : %s/%s/%s %s:%s:%s \n" %(t1[0],t1[1],t1[2],t1[4],t1[5],t1[6]))
        f.close()
        waittime = 1
        while(waittime):
            picosleep.seconds(int(total_sleep))
            waittime = 0
            #t = rtc.datetime()
            t = rtc.read_time()                                
            t1 = [0 for i in range(len(potime))]
            timerefine(t,t1)
            f = open("/sd/timedata" + ("%s%s%s%s%s%s" %(potime1[0],potime1[1],potime1[2],potime1[4],potime1[5],potime1[6])) + ".txt", "a" ,encoding='UTF-8')
            f.write(str(i+1) + " ")
            f.write("bottle end   : %s/%s/%s %s:%s:%s \n" %(t1[0],t1[1],t1[2],t1[4],t1[5],t1[6]))
            f.write("--------------------------------------------------------------- \n")
            f.close()
            motorrun = 1
            while(motorrun):
                RotateCW(cwpwmvalue)
                sleep(0.8)
                circlecheck =  1
                while(circlecheck):
                    if hs.value() == 0:
                        RotateCCW(ccwpwmvalue)
                        sleep(0.1)
                        StopMotor()
                        sleep(0.1)
                        motorrun = 0
                        circlecheck=0

    startflag = 0
f.close()