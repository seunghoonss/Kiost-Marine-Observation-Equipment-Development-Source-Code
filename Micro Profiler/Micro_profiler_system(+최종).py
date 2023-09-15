from machine import Pin, PWM, ADC
import time

from ds3231_i2c import DS3231_I2C
from io import StringIO
#import picosleep

import _thread


led = Pin(25, Pin.OUT)

# 모터1 및 엔코더 설정 # 시계방향 = 정방향
ina1 = Pin(10, Pin.IN) # hall sensor
ina2 = Pin(11, Pin.IN)
mina1 = Pin(14, Pin.OUT) # motor
mina2 = Pin(15, Pin.OUT)
pwma = PWM(Pin(20))
pwma.freq(1000)

# 모터2 및 엔코더 설정 # 시계방향
ina3 = Pin(16, Pin.IN) # hall sensor
ina4 = Pin(17, Pin.IN)
mina3 = Pin(18, Pin.OUT) # motor
mina4 = Pin(19, Pin.OUT)
pwmb = PWM(Pin(21))
pwmb.freq(1000)

# 모터3 및 엔코더 설정 # 시계
ina5 = Pin(8, Pin.IN) # hall sensor
ina6 = Pin(9, Pin.IN)
mina5 = Pin(12, Pin.OUT) # motor
mina6 = Pin(13, Pin.OUT)
pwmc = PWM(Pin(22))
pwmc.freq(1000)

analog_value_1 = machine.ADC(26) # adc converter
analog_value_2 = machine.ADC(27)
analog_value_3 = machine.ADC(28)

outcome = [0, -1, 1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0]  # 엔코더 값에 따른 방향과 회전 방향 결정
last_AB = 0b00
position = 0
No_number = 0
step_value = 0
counter = 0

outcome2 = [0, -1, 1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0]  # 엔코더 값에 따른 방향과 회전 방향 결정
last_AB2 = 0b00
position2 = 0
No_number2 = 0
step_value2 = 0
counter2 = 0

outcome3 = [0, -1, 1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0]  # 엔코더 값에 따른 방향과 회전 방향 결정
last_AB3 = 0b00
position3 = 0
No_number3 = 0
step_value3 = 0
counter3 = 0

# 모터 초기 상태 설정
ina1.value(1)
ina2.value(0)
pwma.duty_u16(0)
mina1.value(1)
mina2.value(0)

ina3.value(1)
ina4.value(0)
pwmb.duty_u16(0)
mina3.value(1)
mina4.value(0)

ina5.value(1)
ina6.value(0)
pwmc.duty_u16(0)
mina5.value(1)
mina6.value(0)

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

# 엔코더 모터 이동 함수
def move1(direction, speed, length):
    global position, last_AB, counter, No_number, step_value
    counter_2 = counter  # counter 펄스(pulses)수

    if direction == 1:  # 정방향
        ina1.value(1)
        ina2.value(0)
        pwma.duty_u16(speed)
        mina1.value(1)
        mina2.value(0)
        OP_value = 1

    elif direction == 0:  # 정지
        ina1.value(0)
        ina2.value(0)
        pwma.duty_u16(speed)
        mina1.value(0)
        mina2.value(0)
        OP_value = 0

    elif direction == -1:  # 역방향
        ina1.value(0)
        ina2.value(1)
        pwma.duty_u16(speed)
        mina1.value(0)
        mina2.value(1)
        OP_value = 1
        counter_2 = -(counter_2)

    while OP_value:
        current_AB = (ina1.value() << 1) | ina2.value() # 홀센서 핀 상태 읽어 변수 저장
        position = (last_AB << 2) | current_AB # 비트 연산 positon 저장
        counter += outcome[position] # 엔코더의 회전 방향에 따라 적절한 값을 가지며, 모터 실제 이동 거리 기록 
        last_AB = current_AB # 이전(최신)상태 저장

        if direction == 1: # 방향에 따라 counter 값 증감
            counter += 1
        else:
            counter -= 1

        if abs(counter) == length + counter_2:
            ina1.value(0)
            ina2.value(0)
            pwma.duty_u16(speed)
            mina1.value(0)
            mina2.value(0)
            step_value += 1

            # 펄스 값을 이용한 계산 및 출력
            pulses = counter
            result_distance_mm = calculate_distance_per_pulse(pulses)
            print("모터 1 펄스 값 {}, 현재 위치 {}단계에 해당하는 이동거리: {:.2f}mm".format(pulses, step_value, result_distance_mm))

            time.sleep(0.5)
            break


# 엔코더 모터2 이동 함수
def move2(direction2, speed2, length2):
    global position2, last_AB2, counter2, No_number2, step_value2
    counter_4 = counter2  # counter 펄스(pulses)수

    if direction2 == 1:  # 정방향
        ina3.value(1)
        ina4.value(0)
        pwmb.duty_u16(speed2)
        mina3.value(1)
        mina4.value(0)
        OP_value = 1

    elif direction2 == 0:  # 정지
        ina3.value(0)
        ina4.value(0)
        pwmb.duty_u16(speed2)
        mina3.value(0)
        mina4.value(0)
        OP_value = 0

    elif direction2 == -1:  # 역방향
        ina3.value(0)
        ina4.value(1)
        pwmb.duty_u16(speed2)
        mina3.value(0)
        mina4.value(1)
        OP_value = 1
        counter_4 = -(counter_4)

    while OP_value:
        current_AB2 = (ina3.value() << 1) | ina4.value() # 홀센서 핀 상태 읽어 변수 저장
        position2 = (last_AB2 << 2) | current_AB2 # 비트 연산 positon 저장
        counter2 += outcome2[position2] # 엔코더의 회전 방향에 따라 적절한 값을 가지며, 모터 실제 이동 거리 기록 
        last_AB2 = current_AB2 # 이전(최신)상태 저장

        if direction2 == 1: # 방향에 따라 counter 값 증감
            counter2 += 1
        else:
            counter2 -= 1

        if abs(counter2) == length2 + counter_4:
            ina3.value(0)
            ina4.value(0)
            pwmb.duty_u16(speed2)
            mina3.value(0)
            mina4.value(0)
            step_value2 += 1

            # 펄스 값을 이용한 계산 및 출력
            pulses2 = counter2
            result_distance_mm = calculate_distance_per_pulse(pulses2)
            print("모터 2 펄스 값 {}, 현재 위치 {}단계에 해당하는 이동거리: {:.2f}mm".format(pulses2, step_value2, result_distance_mm))

            time.sleep(0.5)
            break


# 엔코더 모터3 이동 함수
def move3(direction3, speed3, length3):
    global position3, last_AB3, counter3, No_number3, step_value3
    counter_6 = counter3  # counter 펄스(pulses)수

    if direction3 == 1:  # 정방향
        ina5.value(1)
        ina6.value(0)
        pwmc.duty_u16(speed3)
        mina5.value(1)
        mina6.value(0)
        OP_value = 1

    elif direction3 == 0:  # 정지
        ina5.value(0)
        ina6.value(0)
        pwmc.duty_u16(speed3)
        mina5.value(0)
        mina6.value(0)
        OP_value = 0

    elif direction3 == -1:  # 역방향
        ina5.value(0)
        ina6.value(1)
        pwmc.duty_u16(speed3)
        mina5.value(0)
        mina6.value(1)
        OP_value = 1
        counter_6 = -(counter_6)

    while OP_value:
        current_AB3 = (ina5.value() << 1) | ina6.value() # 홀센서 핀 상태 읽어 변수 저장
        position3 = (last_AB3 << 2) | current_AB3 # 비트 연산 positon 저장
        counter3 += outcome3[position3] # 엔코더의 회전 방향에 따라 적절한 값을 가지며, 모터 실제 이동 거리 기록 
        last_AB3 = current_AB3 # 이전(최신)상태 저장

        if direction3 == 1: # 방향에 따라 counter 값 증감
            counter3 += 1
        else:
            counter3 -= 1

        if abs(counter3) == length3 + counter_6:
            ina5.value(0)
            ina6.value(0)
            pwmc.duty_u16(speed3)
            mina5.value(0)
            mina6.value(0)
            step_value3 += 1

            # 펄스 값을 이용한 계산 및 출력
            pulses3 = counter3
            result_distance_mm = calculate_distance_per_pulse(pulses3)
            print("모터 3 펄스 값 {}, 현재 위치 {}단계에 해당하는 이동거리: {:.2f}mm".format(pulses3, step_value3, result_distance_mm))

            time.sleep(0.5)
            break


# 초기 상태 설정
step_values = [0, 0, 0]  # 각 모터의 현재 단계
total_distances = [0, 0, 0]  # 각 모터의 총 이동 거리


# 모터 이동 제어 함수 (xyz, 방향, 속도, 거리)
def move_motor(motor_index, direction, speed, pulse_count):
    global step_values, total_distances
    step_values[motor_index-1] += 1
    pulses = pulse_count
    result_distance_mm = calculate_distance_per_pulse(pulses) * direction  # 방향에 따라 거리 +, - 적용
    total_distances[motor_index-1] += result_distance_mm

    # 모터 이동 코드
    if motor_index == 1:
        move1(direction, speed, pulse_count)
    elif motor_index == 2:
        move2(direction, speed, pulse_count)
    elif motor_index == 3:
        move3(direction, speed, pulse_count)

def calculate_distance_per_pulse(pulses):
    PPR = 44  # A, B 신호의 상승 엣지와 하강 엣지 모두 사용한 ppr, 아닌경우 22
    gear_ratio = 103  # 기어
    
    step_distance = 360 / (PPR * gear_ratio)  # 1 스텝 당 이동 거리 (degrees)
    gearbox_length_mm = 23  # 기어박스 길이 (mm)
    return (pulses * step_distance / 360) * gearbox_length_mm

# 이 배열은 각 모터의 1펄스당 이동거리(mm)를 나타냅니다. 실제 값은 여러분의 모터 및 설정에 따라 변경됩니다.
distance_per_pulse = [
    0.005075021743774414062500,  # 모터 1의 1펄스당 이동거리(mm)
    0.005075021743774414062500,  # 모터 2의 1펄스당 이동거리(mm)
    0.005075021743774414062500   # 모터 3의 1펄스당 이동거리(mm)
]

# 거리(mm) 펄스값 변환 함수
def calculate_pulse_from_distance(motor_index, distance):
    return int(distance / distance_per_pulse[motor_index-1])


def move_motor_with_distance_limit(motor_index, direction, target_distance):    
    global total_distances
    
    total_distances[motor_index-1] = 0  # 모터의 총 이동 거리 재설정

    speed, _ = motor_configs[motor_index-1]
    pulse_count = calculate_pulse_from_distance(motor_index, target_distance)  # Change from config_distance to target_distance
    
    # 제어 코드 시작
    while abs(total_distances[motor_index-1]) < abs(target_distance):  # Change <= to <
        move_distance = distance_per_pulse[motor_index-1] * pulse_count * direction
        time.sleep(0.1)
            
        if abs(total_distances[motor_index-1] + move_distance) > abs(target_distance):
            pulse_count = int((abs(target_distance) - abs(total_distances[motor_index-1])) / distance_per_pulse[motor_index-1])
            time.sleep(0.1)
            if pulse_count == 0:
                break
        move_motor(motor_index, direction, speed, pulse_count)
    move_motor(motor_index, 0, 0, 0)


# 속도, 거리
# 거리 값 최소 단위 통일 시켜야 됨, limit 거리의 x의 배수관계식
motor_configs = [
    (65535, 20),  # 모터 1
    (65535, 20),  # 모터 2
    (65535, 20)   # 모터 3
]

def main_sequence1():
    print("\n 구역1 측정 시작! \n")
    #move_motor_with_distance_limit(1, +1, 20*1)  # 사이클 1
    move_motor_with_distance_limit(2, +1, 20*3)  # 정방향 모터2, 정방향, 6cm
    move_motor_with_distance_limit(2, -1, 20*3)  # 역방향 모터2, 역방향, -6cm
    
    print("\n 구역2 측정 시작! \n")
    move_motor_with_distance_limit(1, +1, 20*1)  # 사이클 1 모터1, 정방향,  2cm
    move_motor_with_distance_limit(2, +1, 20*3)  # 정방향
    move_motor_with_distance_limit(2, -1, 20*3)  # 역방향
    
    print("\n 구역3 측정 시작! \n")
    move_motor_with_distance_limit(1, +1, 20*1+(0.01))  
    move_motor_with_distance_limit(2, +1, 20*3)  
    move_motor_with_distance_limit(2, -1, 20*3)
    
    print("\n 구역4 측정 시작! \n")
    move_motor_with_distance_limit(1, +1, 20*1)  
    move_motor_with_distance_limit(2, +1, 20*3)  
    move_motor_with_distance_limit(2, -1, 20*3)
    
    print("\n Cycle 반주기 pitch 측정 시작! \n")
    print("\n 구역5 측정 시작! \n")
    move_motor_with_distance_limit(3, +1, 20*1)  # 모터3 모터3, 정방향, 2cm
    move_motor_with_distance_limit(2, +1, 20*3)  # 정방향
    move_motor_with_distance_limit(2, -1, 20*3)  # 역방향    
    
    print("\n 구역6 측정 시작! \n")  
    move_motor_with_distance_limit(1, -1, 20*3) # 동작 에러 
    move_motor_with_distance_limit(1, +1, 20*2) # 동작 에러 # 40mm
    move_motor_with_distance_limit(2, +1, 20*3)  # 정방향
    move_motor_with_distance_limit(2, -1, 20*3)  # 역방향

    print("\n 구역7 측정 시작! \n")
    
    move_motor_with_distance_limit(1, -1, 20*2) # 동작 에러
    
    move_motor_with_distance_limit(1, +1, 20*1) # 동작 에러 # 20mm
    move_motor_with_distance_limit(2, +1, 20*3)  # 정방향
    move_motor_with_distance_limit(2, -1, 20*3)  # 역방향
 
    print("\n 구역8 측정 시작! \n")  
    move_motor_with_distance_limit(1, -1, 20*1) # 동작 에러 
    move_motor_with_distance_limit(1, +1, 20*0) # 동작 에러 # 0mm
    move_motor_with_distance_limit(2, +1, 20*3)  # 정방향
    move_motor_with_distance_limit(2, -1, 20*3)  # 역방향
    move_motor_with_distance_limit(3, -1, 20*1)  
    
    print("\n Cycle 1주기 pitch 측정 완료! \n")

# Main function for all motors
def main():
    main_sequence1()
    

if __name__ == '__main__':  # Call the main function only when this script is run directly
    try:
        main()
    except KeyboardInterrupt:  # ctrl+c
        # Stop all motors
        for motor_index in range(3):
            move_motor(motor_index + 1, 0, 0, 0)


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
