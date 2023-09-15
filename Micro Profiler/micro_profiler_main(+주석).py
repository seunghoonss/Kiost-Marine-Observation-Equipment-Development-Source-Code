from machine import Pin , PWM , I2C, RTC
import time
from ds3231_i2c import DS3231_I2C
from io import StringIO
#import picosleep


led = Pin(25, Pin.OUT)

ina1 = Pin(11,Pin.OUT) # hall sensor
ina2 = Pin(10,Pin.OUT)
mina1 = Pin(14,Pin.OUT) # motor
mina2 = Pin(15,Pin.OUT)
pwma = PWM(Pin(22))
pwma.freq(1000)

analog_value_1 = machine.ADC(26) # adc converter
analog_value_2 = machine.ADC(27)
analog_value_3 = machine.ADC(28)

outcome = [0,-1,1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0]
last_AB = 0b00
#counter = int(start_position) # start position
position = 0
No_number = 0
step_value = 0

# 모터 초기 상태 설정
ina1.value(1)
ina2.value(0)
pwma.duty_u16(100)
mina1.value(1)
mina2.value(0)

# config 파일 변수 저장

def fileopen():
    global interval,wait_time,start_position,step_number,step_distance,huge_time,measure_count,cycle_wait_time,cycle_number
    item = []
    f = open("config_2.cfg", 'r')
    line = f.readlines()
    for i in range(len(line)):
        item.append(line[i].split(" "))
    interval = int(item[0][1])
    wait_time = int(item[1][1])
    start_position = int(item[2][1])
    step_number = int(item[3][1])
    step_distance = int(item[4][1])
    huge_time = int(item[5][1])
    measure_count = int(item[6][1])
    cycle_wait_time = int(item[7][1])
    cycle_number = int(item[8][1])            
    f.close()

# print 된 값을 변수로 저장

def return_print(*message):
    io = StringIO()
    print(*message, file=io, end="")
    return io.getvalue()

# 16진수 변환, 리스트 reverse

def timerefine(variable_a,variable_b) :
    for i in range(len(variable_a)) :
        variable_b[i] = int(return_print("%02x"%variable_a[i]))
    variable_b.reverse()
    variable_b.append(0)
    variable_b[0] = variable_b[0]+2000
    return variable_a,variable_b

# def analog_setting(value_1,value_2,value_3):
#     global analog_value_1,analog_value_2,analog_value_3
#     analog_value_1 = machine.ADC(value_1)
#     analog_value_2 = machine.ADC(value_2)
#     analog_value_3 = machine.ADC(value_3)


# 엔코더 모터 이동 => 방향, 스피드, 길이
    
def move(direction, speed, length): #include analog logging
    global position,current_AB,last_AB,counter,analog_value_1,analog_value_2,analog_value_3,No_number,step_value
    counter_2 = counter # 현재까지 이동한 거리 저장 변수
    if direction == 1: # 정방향 회전
        ina1.value(1)
        ina2.value(0)
        pwma.duty_u16(speed)
        mina1.value(1)
        mina2.value(0)
        OP_value = 1
        
    if direction == 0: # 모터 정지
        ina1.value(0)
        ina2.value(0)
        pwma.duty_u16(speed)
        mina1.value(0)
        mina2.value(0)
        OP_value = 0
        
    if direction == -1: # 역방향 회전
        ina1.value(0)
        ina2.value(1)
        pwma.duty_u16(speed)
        mina1.value(0)
        mina2.value(1)
        OP_value = 1
        counter_2 = -(counter_2)
        
    while (OP_value): # OP_value 변수가 Ture(1) 이면 루프 실행
        current_AB = (ina1.value() <<1) | ina2.value() # 홀센서 핀 상태 읽어 변수 저장
        position = (last_AB << 2) | current_AB # 비트 연산 positon 저장
        counter += outcome[position] # 엔코더의 회전 방향에 따라 적절한 값을 가지며, 모터 실제 이동 거리 기록 
        last_AB = current_AB # 이전(최신)상태 저장
        
        if direction == 1: # 방향에 따라 counter 값 증감
            counter += 1
        else:
            counter += -1
        
#         counter += 1
        
        
        if abs(counter) == length+counter_2: # 같으면 루프 종료
            ina1.value(0) 
            ina2.value(0)
            pwma.duty_u16(speed)
            mina1.value(0)
            mina2.value(0)
            step_value += 1 # 이동 단계 기록
            print("END") # 이동 완료
            break
    
    

"""
startflag = 1
while startflag: # Main
    
#     analog_setting(26,27,28) # analog pin
    fileopen() # config file
    
    ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
    rtc = DS3231_I2C(ds_i2c)
    # 0.63
    potime = rtc.read_time()
    potime1 = [0 for i in range(len(potime))]
    timerefine(potime,potime1) # potime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
    #file write
    f = open("loggingdata"+str(potime1[0])+str(potime1[1])+str(potime1[2])+str(potime1[4])+str(potime1[5])+str(potime1[6]),"w")
    f.write("Micro_Profiler_2022 \n")
    f.write("DATE: "+str(potime1[0])+"-"+str(potime1[1])+"-"+str(potime1[2])+"\n")   
    f.write("TIME: "+str(potime1[4])+":"+str(potime1[5])+":"+str(potime1[6])+"\n")
    
    f.write("INTERVAL: "+str(interval)+" "+str(interval*100)+"ms\n")
    f.write("(START)WAIT_TIME: "+str(wait_time)+" MIN\n")
    f.write("START_POSITION: "+str(start_position)+" um\n")
    f.write("STEP_NUMBER: "+str(step_number)+"\n")
    f.write("STEP_DISTANCE: "+str(step_distance)+" um\n")
    f.write("HUGE_TIME: "+str(huge_time)+" SEC\n")
    f.write("MEASURE_COUNT: "+str(measure_count)+" SEC\n")
    f.write("CYCLE_WAIT_TIME: "+str(cycle_wait_time)+" MIN\n")
    f.write("CYCLE_NUMBER: "+str(cycle_number)+"\n")
    f.write("\n")
    f.write("No Cycle Step Current1 Current2 Current3 Current4\n")
    f.close()
    
    led.toggle()
    
    picosleeptime = int(wait_time)*60
#     picosleep.seconds(picosleeptime)
    time.sleep(1)
    
    led.toggle()
    
#     f = open("loggingdata"+str(potime1[0])+str(potime1[1])+str(potime1[2])+str(potime1[4])+str(potime1[5])+str(potime1[6]),"a")       
    redflag = 1
    while redflag:
        for i in range(cycle_number):
            blueflag = 1
            step_value = 0
            while blueflag:
                if step_value == step_number+1:
                    step_value = 0
                    move(-1,20000,counter)
                    print(counter)
                    time.sleep(cycle_wait_time*60)
                    
                    break
                
                f = open("loggingdata"+str(potime1[0])+str(potime1[1])+str(potime1[2])+str(potime1[4])+str(potime1[5])+str(potime1[6]),"a")
                
                move(1,20000,int(step_distance)*3)#step distance advance
                print(counter)
                time.sleep(int(huge_time))#huge time sleep
                
                while_count = 0
                while True:
                    reading_1 = analog_value_1.read_u16()
                    reading_2 = analog_value_2.read_u16()
                    reading_3 = analog_value_3.read_u16()
                    
                    if while_count == 0 :
                        retime = rtc.read_time()
                        retime1 = [0 for i in range(len(retime))]
                        timerefine(retime,retime1) # retime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
                        f.write(str(No_number)+" "+str(int(i)+1)+" "+str(step_value-1)+" "+str(reading_1)+
                                " "+str(reading_2)+" "+str(reading_3)+" "+str(retime1[4])+":"+str(retime1[5])+":"+str(retime1[6]))
                        f.write("\n")
                    else:                        
                        f.write(str(No_number)+" "+str(int(i)+1)+" "+str(step_value-1)+" "+str(reading_1)+" "+str(reading_2)+" "+str(reading_3))
                        f.write("\n")
                    
                    No_number += 1               
                    while_count += 1
                    
                    time.sleep(int(interval)*0.1)
                    if while_count == int(measure_count):
                        f.close()
                        break
            
                
                
                
        
            
        
#         retime = rtc.read_time()
#         retime1 = [0 for i in range(len(retime))]
#         timerefine(retime,retime1) # retime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
        
        
        
    
        f.close()
        redflag = 0
        startflag = 0
        

"""