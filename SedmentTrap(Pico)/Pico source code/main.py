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

spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
sd = sdcard.SDCard(spi, Pin(13))
vfs = os.VfsFat(sd)

os.mount(sd, '/sd')

"""
##motor driver pin set A motor
ina1 = Pin('X3', Pin.OUT_PP)
ina2 = Pin('X2', Pin.OUT_PP)
#pwma = Pin('Y3', Pin.OUT_PP)
#pwma.high()


pwma = Pin('X1') # X1 has TIM2, CH1
"""
#motor driver pin set A motor
ina1 = Pin(14,Pin.OUT)#motor
ina2 = Pin(15,Pin.OUT)  
pwma = PWM(Pin(26))
pwma.freq(1000)


"""
tim = Timer(2, freq=1000)
ch = tim.channel(1, Timer.PWM, pin=pwma)
ch.pulse_width_percent(50)

accel = pyb.Accel()
"""
#Gyro Sensor Setting
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
sensor = MPU9250(i2c)

ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
rtc = DS3231_I2C(ds_i2c)

# program config - setting cycle time file open
timecyclehourindex = 0
timecycledayindex = 0
timecycleminuteindex = 0
sleepcount = 0

#rtc = machine.RTC()

f = open("config.cfg", 'r')
line = f.readlines()
for line in line:
    item = line.split(" ")
    delaytimeminute = item[item.index("startdelaytimeminute")+1]
    timecycleindex = item[item.index("on")+1]
    timecyclevalue = item[item.index("on")+2]
f.close()

timecyclevalue = int(timecyclevalue)

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

"""
##magnet sensor pin set
magVCC = Pin('Y5', Pin.OUT_PP)
magVCC.high()
magGND = Pin('Y6', Pin.OUT_PP)
magGND.low()
magsense = Pin('Y7',  Pin.IN, Pin.PULL_UP) # magnet sensor VCC ON
"""
#Hall sensor
hs=Pin(22,Pin.IN)


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
"""
def RotateCW(duty):
    ina1.value(1)
    ina2.value(0)
#     duty_16 = int((duty*65536)/125)
#     pwma.duty_u16(duty_16)
    ch.pulse_width_percent(100)
    
def RotateCCW(duty):
    ina1.value(0)
    ina2.value(1)
    #duty_16 = int((duty*65536)/100)
#     duty_16 = int((duty*65536)/800)
#     pwma.duty_u16(duty_16)
    ch.pulse_width_percent(10)
        
def StopMotor():
    ina1.value(0)
    ina2.value(0)
#     pwma.duty_u16(0)
    ch.pulse_width_percent(0)

def CWStopMotor(duty):
    ina1.value(0)
    ina2.value(1)
#     pwma.duty_u16(10)
    sleep(1)

def CCWStopMotor(duty):
    ina1.value(1)
    ina2.value(0)
#     pwma.duty_u16(10)
    sleep(1)
"""
#motor PWM duty set
duty_cycle = 100




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
            RotateCW(duty_cycle)
            sleep(0.8)
            circlecheck =  1
            while(circlecheck):
                if hs.value() == 0:
                    RotateCCW(duty_cycle)
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
                RotateCW(duty_cycle)
                sleep(0.8)
                circlecheck =  1
                while(circlecheck):
                    if hs.value() == 0:
                        RotateCCW(duty_cycle)
                        sleep(0.1)
                        StopMotor()
                        sleep(0.1)
                        motorrun = 0
                        circlecheck=0

    startflag = 0
f.close()















