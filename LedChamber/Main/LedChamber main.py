from machine import UART, Pin, PWM , I2C, RTC
import time
from ds3231_i2c import DS3231_I2C
from io import StringIO
import picosleep
import os
from RTC_HAT_TEST import RTC_HAT
import binascii



def fileopen():
    global wait_time,led_value,cycle_count,stir_pump_rate,led_rate
    item = []
    f = open("led_config.cfg", 'r')
    line = f.readlines()
    for i in range(len(line)):
        item.append(line[i].split(" "))
    wait_time = int(item[0][1])
    
    led_rate = int(item[1][1])
    led_value = []
    
    for i in range(led_rate):
        led_value.append(round(100/led_rate*i,3)) # Round to the third digit
    led_value.append(100)
            
    cycle_count = int(item[2][1])    
    stir_pump_rate = int(item[3][1])
    f.close()
    
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


def led_control(pwm_percent): #LED
    
    pwma = PWM(Pin(27))
    pwma.freq(1000)
    
    pwm_value = (pwm_percent * 0.01)*led_pwm_int*655.35
    pwma.duty_u16(int(pwm_value))
    
def oxyzen_sensor_start():
    global uart0
    uart0 = machine.UART(0, 19200) #Oxyzen Sensor UART
    txData = "mode0000\r\n"  
    
    uart0.write("\r")
    uart0.write(txData)
    
    time.sleep(1)
    
    uart0.write("\r")
    uart0.write(txData)
    
    time.sleep(1)
    

    

    
def stir_motor_start(pump_rate):
    global pwmb
    mina1 = Pin(20,Pin.OUT)#motor
    mina2 = Pin(21,Pin.OUT)
        
    pwmb = PWM(Pin(26))
    pwmb.freq(1000)
    
    pwmb.duty_u16(int((pump_rate*0.01)*65535))
    mina1.value(1)
    mina2.value(0)
    
    
def led_pwm_check():
    global led_pwm_int
    item_2 = []
    fc = open("led_pwm_config.cfg","r")
    line = fc.readlines()
    for i in range(len(line)):
        item_2.append(line[i].split(" "))
    led_pwm_int = int(item_2[0][1])
    fc.close()

led_pwm_check()
led_control(0)
time.sleep(5)



# gui start
gui_flag = 1
gui_count = 0
gui_list = []

uart1 = machine.UART(1, 19200) #Oxyzen Sensor UART
gui_led = Pin(25, Pin.OUT)


ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
rtc = DS3231_I2C(ds_i2c)
   
"""
potime = rtc.read_time()
    
potime1 = [0 for i in range(len(potime))]
timerefine(potime,potime1) # potime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
print(str(potime1[0]))
print("{:0>2}".format(str(potime1[1])))
print("{:0>2}".format(str(potime1[2])))
print("{:0>2}".format(str(potime1[4])))
print("{:0>2}".format(str(potime1[5])))
print("{:0>2}".format(str(potime1[6])))

#print(str(potime1[0])+"{:0<2}".format(str(potime1[1]))+str(potime1[2])+str(potime1[4])+str(potime1[5])+str(potime1[6]))
"""
while(gui_flag):
    try:
        while True:
            gui_count += 1
            print(gui_count)
            if gui_count == 30:
                
                gui_flag = 0
                break           
            rxData = uart1.read()
            if not rxData == None:              
                data = rxData.decode('utf-8')
                if data == "start":
                    uart1.write("CONNECT_SUCCESS")
                    gui_led.toggle()
                    time.sleep(0.1)
                                        
                    while True:
                        try:
                            rxData = uart1.read()
                            data = rxData.decode('utf-8')
                            time.sleep(0.2)
                            
                            if data == "start":
                                uart1.write("CONNECT_SUCCESS")
                                gui_led.toggle()
                                
                            if data == "config_check":                        
                                fileopen()
                                uart1.write(str(wait_time)+" "+str(led_rate)+" "+str(cycle_count)+" "+str(stir_pump_rate)+" ")
                                gui_led.toggle()
                                
                            if data == "config_save":     
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                
                                f = open("led_config.cfg","w")
                                data_2 = data.split()
                                f.write("waiting_time "+str(data_2[0])+" minute\n")
                                f.write("led_rate "+str(data_2[1])+"\n")
                                f.write("cycle_count "+str(data_2[2])+" (10second)\n")
                                f.write("stir_pump_pwm "+str(data_2[3]))
                                f.close()
                                gui_led.toggle()
                                
                            if data == "data_name":
                                
                                file_list = os.listdir('./ledchamber_loggingdata')
                                for i in range(len(file_list)):
                                    uart1.write(str(file_list[i]))
                                    time.sleep(0.1)
                                    uart1.write(" ")
                                gui_led.toggle()
                                
                            if data == "data_transfer":
                                
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                
                                file_name = "/ledchamber_loggingdata/"+ data
                                loggingfileMatrix = []
                                

                                with open(file_name) as file :
                                    for lineContent in file: # Point.1
                                        loggingfileMatrix.append(lineContent.strip('\n'))
                        
                                for i in range(len(loggingfileMatrix)):
                                    uart1.write(str(loggingfileMatrix[i]))
                                    uart1.write("\n")
                                    #time.sleep(0.02)
                                    time.sleep(0.1)
                                
                                
                                uart1.write("\n")
                                uart1.write("END")
                                
                                gui_led.toggle()
                                
                                
                            if data == "led_control":
                                
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                
                                time.sleep(0.05)
                                
                                led_control(int(data))
                                gui_led.toggle()
                                
                                
                            if data == "motor_pwm_control":
                            
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                print(data)
                                time.sleep(0.05)
                                
                                stir_motor_start(int(data))
                                
                            if data == "led_pwm_save":
                                
                                rxData = uart1.read()
                                data = rxData.decode('utf-8')
                                
                                time.sleep(0.05)                                
                                
                                fc = open("led_pwm_config.cfg","w")
                                fc.write("led_pwm " + str(data))
                                fc.close()
                                
                                
                            if data == "time_check":
                                
                                ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
                                rtc = DS3231_I2C(ds_i2c)

                                potime = rtc.read_time()                                
                                potime1 = [0 for i in range(len(potime))]
                                timerefine(potime,potime1) # potime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
                                
                                uart1.write(str(potime1[0])+" "+"{:0>2}".format(str(potime1[1]))+" "+"{:0>2}".format(str(potime1[2]))+" "+"{:0>2}".format(str(potime1[3]))+" "+"{:0>2}".format(str(potime1[4]))+" "+"{:0>2}".format(str(potime1[5]))+" "+"{:0>2}".format(str(potime1[6])))
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
                                
                                
                            if data == "OxCheck":
                                oxyzen_sensor_start()
                                redflag=1
                                while redflag:
                                    
                                    rxData = uart0.read()
                                    if not rxData == None:
                                        data = rxData.decode('utf-8')
                                        uart1.write(data)
                                        redflag=0

         
                        except Exception as e :
                            continue
                        
#                     gui_led.toggle()
               

            time.sleep(1)
        
    except Exception as e :
        continue
        
    


    

# main
startflag = 1


while startflag:
    fileopen()
    
    ds_i2c = I2C(1,sda=Pin(6), scl=Pin(7))
    rtc = DS3231_I2C(ds_i2c)
    
    No_count = 0
    
    rxData_list = []
    ps_list_T = []
    ps_list_O = []
    
    potime = rtc.read_time()
    
    potime1 = [0 for i in range(len(potime))]
    timerefine(potime,potime1) # potime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
    
    f = open("./ledchamber_loggingdata/ledchamber_loggingdata"+str(potime1[0])+"{:0>2}".format(str(potime1[1]))+"{:0>2}".format(str(potime1[2]))+"{:0>2}".format(str(potime1[4]))+"{:0>2}".format(str(potime1[5]))+"{:0>2}".format(str(potime1[6])),"w")
    f.write("LED_CHAMBER_2022 \n")
    f.write("DATE: "+str(potime1[0])+"-"+"{:0>2}".format(str(potime1[1]))+"-"+"{:0>2}".format(str(potime1[2]))+"\n")   
    f.write("TIME: "+"{:0>2}".format(str(potime1[4]))+":"+"{:0>2}".format(str(potime1[5]))+":"+"{:0>2}".format(str(potime1[6]))+"\n")
    
    f.write("(START)WAIT_TIME: "+str(wait_time)+" MIN\n")
    f.write("LED_RATE: "+str(led_rate)+"\n")
    f.write("LED_VALUE: ")
    for i in range(len(led_value)-1):
        
        
        f.write(str(led_value[i])+" ")
        
    f.write(str(led_value[-1]))
    f.write("\n")
    f.write("CYCLE_COUNT: "+str(cycle_count)+" CYCLE_MINUTE: "+str((round(cycle_count/6,3)))+" MINUTE\n")
    f.write("STIR_PUMP_RATE: "+str(stir_pump_rate)+" ML/MIN\n")
    f.write("\n")
    f.write("NO LED_RATE NO_CYCLE DATE TIME OXYZEN_VALUE TEMP_VALUE\n")
    f.close()
    
    
    picosleeptime = int(wait_time)*60 #wait time sleep
    picosleep.seconds(picosleeptime)
    time.sleep(1)
    
    
    
    
    
    for j in range(led_rate+1):
        No_cycle = 0
        if j == 0:
            stir_motor_start(stir_pump_rate)
            time.sleep(1)
            
            
        led_control(led_value[j])
        time.sleep(1)
        oxyzen_sensor_start() # oxyzen sensor start
        
        redflag = 1
        while redflag:
            
            try:
                if No_count == cycle_count*(j+1):
                    redflag = 0
                    ps_list_T.clear()
                    ps_list_O.clear()
                    
                    break
                
                
                rxData = uart0.read()

                
                if not rxData == None:
                    
                    data = rxData.decode('utf-8')
                    data_index_T = int(data.index('T'))
                    data_index_O = int(data.index('O'))
                    ps_list_T.append(data[data_index_T+1:data_index_T+5])#['2999', '3012']
                    ps_list_O.append(data[data_index_O+1:data_index_O+7])#['2454', '2474']
                    
#                     print("NO: "+str(No_count))
#                     print("LED_Value: "+str(led_value[j]))
#                     print("Temp: ",ps_list_T[0])
#                     print("Oxyzen: ",ps_list_O[0])
#                     print("===============\n")
                    
                    f = open("./ledchamber_loggingdata/ledchamber_loggingdata"+str(potime1[0])+"{:0>2}".format(str(potime1[1]))+"{:0>2}".format(str(potime1[2]))+"{:0>2}".format(str(potime1[4]))+"{:0>2}".format(str(potime1[5]))+"{:0>2}".format(str(potime1[6])),"a")
                
                    retime = rtc.read_time()
                    retime1 = [0 for i in range(len(retime))]
                    timerefine(retime,retime1) # retime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
                        
                    f.write(str(No_count+1)+" "+str(j)+" "+str(No_cycle+1)+" "+str(retime1[0])+"-"+"{:0>2}".format(str(retime1[1]))+"-"+"{:0>2}".format(str(retime1[2]))+" "+
                            "{:0>2}".format(str(retime1[4]))+":"+"{:0>2}".format(str(retime1[5]))+":"+"{:0>2}".format(str(retime1[6]))+" "+str(float(int(ps_list_O[0])/100))+" "+str(float(int(ps_list_T[0])/100))+"\n")   
                    f.close()
                    No_count += 1
                    No_cycle += 1
                    ps_list_T.clear()
                    ps_list_O.clear()
                    data = ""
                    
                    
                time.sleep(0.1)
                
                
                            
#             except AttributeError :
#                 continue
            
            except Exception as e :
                continue
            
            
    led_control(0)
    stir_motor_start(0)
    No_cycle = 1
    
    while True:
        try:
            
                
            rxData = uart0.read()
                
            if not rxData == None:
                    
                data = rxData.decode('utf-8')
                data_index_T = int(data.index('T'))
                data_index_O = int(data.index('O'))
                ps_list_T.append(data[data_index_T+1:data_index_T+5])#['2999', '3012']
                ps_list_O.append(data[data_index_O+1:data_index_O+7])#['2454', '2474']
                    
#                 print("NO: "+str(No_count))
#                 print("LED_Value: "+str(led_value[j]))
#                 print("Temp: ",ps_list_T[0])
#                 print("Oxyzen: ",ps_list_O[0])
#                 print("===============\n")
                    
                f = open("./ledchamber_loggingdata/ledchamber_loggingdata"+str(potime1[0])+"{:0>2}".format(str(potime1[1]))+"{:0>2}".format(str(potime1[2]))+"{:0>2}".format(str(potime1[4]))+"{:0>2}".format(str(potime1[5]))+"{:0>2}".format(str(potime1[6])),"a")
                
                retime = rtc.read_time()
                retime1 = [0 for i in range(len(retime))]
                timerefine(retime,retime1) # retime1 : realtime list - [2022, 6, 27, 2, 13, 40, 36, 0]
                        
                f.write(str(No_count+1)+" X "+str(No_cycle)+" "+str(retime1[0])+"-"+"{:0>2}".format(str(retime1[1]))+"-"+"{:0>2}".format(str(retime1[2]))+" "+
                        "{:0>2}".format(str(retime1[4]))+":"+"{:0>2}".format(str(retime1[5]))+":"+"{:0>2}".format(str(retime1[6]))+" "+str(float(int(ps_list_O[0])/100))+" "+str(float(int(ps_list_T[0])/100))+"\n")   
                f.close()
                No_count += 1
                No_cycle += 1
                ps_list_T.clear()
                ps_list_O.clear()
                data = ""
                time.sleep(0.5)
                    
            time.sleep(0.5)
                
                            
        except Exception as e :
                continue
        
    startflag = 0




    






