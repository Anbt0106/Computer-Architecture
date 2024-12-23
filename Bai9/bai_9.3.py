import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

SERVO = 6
LIGHT_SS = 5
PWM = 24
DIR = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(SERVO, GPIO.OUT)
GPIO.setup(LIGHT_SS, GPIO.IN)

pwm_dc = GPIO.PWM(PWM, 1000)
pwm_dc.start(0)

pwm_servo = GPIO.PWM(SERVO, 50) 
pwm_servo.start(0)

curtain_is_open = None


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)


def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def set_servo_angle(angle):
    duty = angle / 18 + 2
    pwm_servo.ChangeDutyCycle(duty)
    time.sleep(1)
    pwm_servo.ChangeDutyCycle(0)


def motor_control(speed, dir):
    GPIO.output(DIR, dir)
    if dir == 0:
        speed = speed
    else:
        speed = 100 - speed
    pwm_dc.ChangeDutyCycle(speed)


def main():
    global curtain_is_open
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    while True:
        light_status = GPIO.input(LIGHT_SS)
        if light_status and curtain_is_open != False:
            lcd_display_string('Dark: Close curtain', 1)
            set_servo_angle(30) # 30 degree
            motor_control(0, 1) # 60% speed, reverse
            time.sleep(3)
            motor_control(0, 0)
            curtain_is_open = False

        elif not light_status and curtain_is_open != True:
            lcd_display_string('Light: Open curtain', 1)
            set_servo_angle(120)
            motor_control(60, 0)
            time.sleep(3)
            motor_control(0, 0)
            curtain_is_open = True
        time.sleep(1)


try:
    main()
except KeyboardInterrupt:
    pwm_dc.stop()
    pwm_servo.stop()
    lcd_clear()
    GPIO.cleanup()
