from datetime import datetime
import serial
import time
import RPi.GPIO as GPIO



motorA_1 = 1
motorA_2 = 7
motorB_1 = 8
motorB_2 = 25

FmotorA_1 = 26
FmotorA_2 = 19
FmotorB_1 = 6
FmotorB_2 = 5


Buzzer = 0

pwm1_pin=12
pwm2_pin=13

GPIO.setmode(GPIO.BCM)
#GPIO.setup(2,GPIO.OUT)
GPIO.setup(pwm1_pin,GPIO.OUT)
GPIO.setup(pwm2_pin,GPIO.OUT)
GPIO.setup(motorA_1,GPIO.OUT)
GPIO.setup(motorA_2,GPIO.OUT)
GPIO.setup(motorB_1,GPIO.OUT)
GPIO.setup(motorB_2,GPIO.OUT)

GPIO.setup(FmotorA_1,GPIO.OUT)
GPIO.setup(FmotorA_2,GPIO.OUT)
GPIO.setup(FmotorB_1,GPIO.OUT)
GPIO.setup(FmotorB_2,GPIO.OUT)

GPIO.setup(Buzzer,GPIO.OUT)

GPIO.output(motorA_1,GPIO.HIGH)
GPIO.output(motorA_2,GPIO.LOW)

GPIO.output(motorB_1,GPIO.LOW)
GPIO.output(motorB_2,GPIO.HIGH)

GPIO.output(FmotorA_1,GPIO.HIGH)
GPIO.output(FmotorA_2,GPIO.LOW)

GPIO.output(FmotorB_1,GPIO.LOW)
GPIO.output(FmotorB_2,GPIO.HIGH)
GPIO.output(Buzzer,GPIO.HIGH)



#PWM(pin,Hz)
pi_pwm1=GPIO.PWM(pwm1_pin,1000)
pi_pwm2=GPIO.PWM(pwm2_pin,1000)


pi_pwm1.start(0)
pi_pwm2.start(0)

pi_pwm1.ChangeDutyCycle(0) #set pwm1 percent
pi_pwm2.ChangeDutyCycle(0) #set pwm2 percent
"""
pi_pwm = GPIO.PWM(2,1000)		#create PWM instance with frequency
pi_pwm.start(0)
"""
cnt=0
while(1):
    GPIO.output(Buzzer,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(Buzzer,GPIO.LOW)
    time.sleep(1)
    """cnt+=1
    if cnt==30:
         cnt=0
         time.sleep(0.5)"""
         
    
    