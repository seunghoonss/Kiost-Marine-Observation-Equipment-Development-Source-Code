from machine import UART, Pin, PWM , I2C, RTC
import time
from ds3231_i2c import DS3231_I2C
from io import StringIO
import picosleep

def led_control(pwm_percent): #LED
    
    pwma = PWM(Pin(27))
    pwma.freq(1000)
    
    pwm_value = (pwm_percent * 0.01)*65535
    pwma.duty_u16(int(pwm_value))
    
def oxyzen_sensor_start():
    global uart0
    uart0 = machine.UART(0, 19200) #Oxyzen Sensor UART
    txData = "repo\r\n"  
    
    uart0.write("\r")
    uart0.write(txData)
    
def stir_motor_start(pump_rate):
    global pwmb
    mina1 = Pin(20,Pin.OUT)#motor
    mina2 = Pin(21,Pin.OUT)
        
    pwmb = PWM(Pin(26))
    pwmb.freq(1000)
    
    
    pwmb.duty_u16(int((pump_rate*0.01)*65535))
    mina1.value(1)
    mina2.value(0)
    
    
    
stir_motor_start(0)


oxyzen_sensor_start() #마지막이 초록


led_control(0)


while True:
    rxData = uart0.read()
    
    if not rxData == None:
        print(rxData)
    time.sleep(0.1)





















