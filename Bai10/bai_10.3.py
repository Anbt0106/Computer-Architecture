import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}  # LCD PINS
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

RELAY_1 = 12

TRIG = 15
ECHO = 4

LED = 13

PWM_PIN = 24
DIR_PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(RELAY_1, GPIO.OUT)
GPIO.output(LED, GPIO.OUT)
GPIO.setup(LED, False)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(TRIG, False)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

pwm = GPIO.PWM(PWM_PIN, 1000)  # 1000 Hz
pwm.start(0)


def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    if direction == 0:  # nếu direction = 0 thì speed = speed
        speed = speed
    else:  # nếu direction = 1 thì speed = 100 - speed
        speed = 100 - speed
    pwm.ChangeDutyCycle(speed)  # thay đổi duty cycle của pwm


def cal_distance():
    global distance  # khai báo biến distance là biến toàn cục
    print('Calculating distance...')
    time.sleep(1)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # vận tốc âm thanh = 343 m/s = 17150 cm/s
    distance = round(distance, 2)
    return distance


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


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    global pulse_end

    while True:
        cal_distance()
        if distance > 100:
            lcd_clear()
            lcd_display_string('Error', 1)
        else:
            lcd_display_string(f'Distance: {distance} cm', 1)
            if distance > 30:
                GPIO.output(LED, GPIO.LOW)
                motor_control(0, 0)
                GPIO.output(RELAY_1, GPIO.LOW)
                lcd_display_string("Binh thuong", 2)
            elif distance > 20:
                GPIO.output(LED, GPIO.HIGH)
                motor_control(0, 0)
                GPIO.output(RELAY_1, GPIO.HIGH)
                lcd_display_string("Warning 1", 2)
            elif distance > 15:
                GPIO.output(LED, GPIO.HIGH)
                motor_control(0, 0)
                GPIO.output(RELAY_1, GPIO.HIGH)
                lcd_display_string("Warning 2", 2)
            elif distance < 10:
                GPIO.output(LED, GPIO.HIGH)
                motor_control(100, 0)
                GPIO.output(RELAY_1, GPIO.HIGH)
            lcd_display_string("Warning 3", 2)
        time.sleep(0.1)


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
