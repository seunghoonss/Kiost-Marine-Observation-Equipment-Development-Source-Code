from datetime import datetime
import serial
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT) #s1
GPIO.setup(20,GPIO.OUT) #s2
GPIO.setup(21,GPIO.OUT) #s3

ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 19200,
        parity=serial.PARITY_NONE,       
        stopbits=serial.STOPBITS_ONE, 
        bytesize=serial.EIGHTBITS,        
        timeout=0
    )
ser.flush()

def change_channel(number):
    number = number - 1
    income = number // 4
    if income == 1:
        GPIO.output(21,True)
        number = number - 4
    else:
        GPIO.output(21,False)
    income = number // 2
    if income == 1:
        GPIO.output(20,True)
        number = number - 4
    else:
        GPIO.output(20,False)
    income = number % 2
    if income == 1:
        GPIO.output(16,True)
        number = number - 4
    else:
        GPIO.output(16,False)
        
    time.sleep(1)
    
def start_mode():
    change_channel(1)
    ut = "mode0001"
    ser.write("\r".encode('utf-8'))
    ser.write((ut+"  "+"\r").encode('utf-8'))

    time.sleep(0.5)
    change_channel(2)
    ser.write("\r".encode('utf-8'))
    ser.write((ut+"  "+"\r").encode('utf-8'))
    
# start_mode()
# change_channel(2)

# change_channel(2)
# ut = "mode0001"
# ser.write("\r".encode('utf-8'))
# ser.write((ut+"  "+"\r").encode('utf-8'))
# 
# time.sleep(1)
# change_channel(2)
# ser.write("\r".encode('utf-8'))
# ser.write((ut+"  "+"\r").encode('utf-8'))
#

# now = datetime.now()
# print(now)
# change_channel(7)
# pump_ml = 10
# pump_order = "D,"+str(pump_ml)+"\r"
# ser.write(pump_order.encode('utf-8'))

change_channel(8)
pump_order = "X"+"\r"
ser.write("\r".encode('utf-8'))
ser.write(pump_order.encode('utf-8'))




# while(1):
#     x = ser.readline().decode()
#     print(x)
#     time.sleep(1)

# change_channel(2)
# ser.write("\r".encode('utf-8'))
# ser.write((ut+"  "+"\r").encode('utf-8'))



# GPIO.output(16,False)
# GPIO.output(20,True)
# GPIO.output(21,True)
# time.sleep(1)
#

# change_channel(5)
# ut = "X"
# ser.write("\r".encode('utf-8'))
# ser.write((ut+"  "+"\r").encode('utf-8'))
# #
# os_list_3 = []
# data_inform = []
# change_channel(3)
# 
# while(1):
#     a = 1
#     change_channel(3)
#     while(a):
#         ser.baudrate = 9600
#         try :
#             z = ser.readline().decode('ascii')
#             os_list_3.append(z)
#             for z in os_list_3 :
#                 if "@T" in z:
#                     data = z
#                     data_inform = data.split(',')
#                     print(float(data_inform[4]))
#                     a = 0
#             os_list_3.clear()
#             data_inform.clear()
#             time.sleep(1)
#         except UnicodeDecodeError:        
#             continue

# while(1):
#     ser.baudrate = 9600
#     time.sleep(1)
#     change_channel(3)
#     x  = ser.readline().decode('ascii')
#     print(x)
#     time.sleep(1)
#     change_channel(4)
#     ser.baudrate = 19200
#     time.sleep(1)
    
#     time.sleep(1)
#     pump_order = "X"+"\r"
#     ser.write(pump_order.encode('utf-8'))
#     time.sleep(1)
#     ser.baudrate = 19200
#         
#     print("change")
#     time.sleep(1)
#     ser.baudrate = 19200
#     time.sleep(1)

#     
#     
#     ser.baudrate = 19200
    
#     ser = serial.Serial(
#         port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
#         baudrate = 19200,
#         parity=serial.PARITY_NONE,       
#         stopbits=serial.STOPBITS_ONE, 
#         bytesize=serial.EIGHTBITS,        
#         timeout=0
#     )
#     ser.flush()

# GPIO.output(16,True)
# GPIO.output(20,True)
# GPIO.output(21,False)
# 
# GPIO.output(16,False)
# GPIO.output(20,False)
# GPIO.output(21,True)
# 
# order = "C"+"\r"
# ser.write(order.encode('utf-8'))
# 
# while(1):
#     x = ser.readline().decode()
#     print(x)
#     time.sleep(1)

# 
# time.sleep(2)
# mm = "D,15"
# pump_order = mm +"\r"
# 
# ser.write(pump_order.encode('utf-8'))

# while(1):
#     x = ser.readline().decode()
#     print(x)
#     

# GPIO.output(18,False)
# 
# time.sleep(1)
# 
# ut = "mode0000"
# ser.write("\r".encode('utf-8'))
# ser.write((ut+"  "+"\r").encode('utf-8'))
# 
# 
# time.sleep(1)
# 
# GPIO.output(18,True)
# 
# ut = "mode0000"
# ser.write("\r".encode('utf-8'))
# ser.write((ut+"  "+"\r").encode('utf-8'))
# 
# 
# time.sleep(1)
# 
# GPIO.output(18,False)
# 
# top = 1
# top_2 = 0
# os_list = []
# 
# data = 0
# data_index_T = 0
# data_index_O = 0
# ps_list_T = []
# ps_list_O = []
# 
# while(top):
#     x = ser.readline().decode()
#     os_list.append(x)
#     for x in os_list :
#         if "N" in x:
#             now = datetime.now()
#             print("now 1 : ", now)
#             data = x
#             data_index_T = int(data.index('T'))
#             data_index_O = int(data.index('O'))
#             ps_list_T.append(data[data_index_T+1:data_index_T+5])#['2999', '3012']
#             ps_list_O.append(data[data_index_O+1:data_index_O+7])#['2454', '2474']
#             print("x : ",data)
#             print("T1 : ",ps_list_T[0])
#             print("O1 : ",ps_list_O[0])
#             GPIO.output(18,True)
#             top_2 = 1
#     os_list.clear()
#     ps_list_T.clear()
#     ps_list_O.clear()
#     
#     while(top_2):
#         x = ser.readline().decode()
#         os_list.append(x)
#         for x in os_list :
#             if "N" in x:
#                 now = datetime.now()
#                 print("now 2 : ", now)
#                 data = x
#                 data_index_T = int(data.index('T'))
#                 data_index_O = int(data.index('O'))
#                 ps_list_T.append(data[data_index_T+1:data_index_T+5])#['2999', '3012']
#                 ps_list_O.append(data[data_index_O+1:data_index_O+7])#['2454', '2474']
#                 print("x : ",data)
#                 print("T1 : ",ps_list_T[0])
#                 print("O1 : ",ps_list_O[0])
#                 GPIO.output(18,False)
#                 top_2 = 0
#         os_list.clear()
#         ps_list_T.clear()
#         ps_list_O.clear()
#     
#      
#     
#     
#     
#     
#     