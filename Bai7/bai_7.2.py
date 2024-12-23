import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BT_1 = 21
BT_2 = 26

PWM_PIN = 24
DIR_PIN = 25

GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

speed = 0
count = 0
count_1 = 0
direction = 0


def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    if direction == 0:
        speed = speed
    else:
        speed = 100 - speed
    pwm.ChangeDutyCycle(speed)


def button_1_pressed():
    global count, speed
    count += 1
    speed += 20
    if count == 4:
        count = 0
        speed = 0
    if speed > 100:
        speed = 100
    motor_control(speed, 0)


def button_2_pressed():
    global speed, count_1
    count_1 += 1
    speed += 20
    if count_1 == 4:
        count_1 = 0
        speed = 0
    if speed >= 100:
        speed = 100
    motor_control(speed, 1)


def main():
    motor_control(0, 0)
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            button_1_pressed()
            print(f'Button 1 pressed {count} times')
            time.sleep(0.25)

        if GPIO.input(BT_2) == GPIO.LOW:
            button_2_pressed()
            print(f'Button 2 pressed {count_1} times')
            time.sleep(0.25)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
