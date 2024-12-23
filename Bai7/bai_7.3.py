import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS = {'BT_1': 21, 'BT_2': 20, 'BT_3': 26}
PWM_PIN = 24
DIR_PIN = 25
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)
speed = 0
count = 0
count_1 = 0
direction = 0


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


def pull_up_bts():
    for pin in BTS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    if direction == 0:
        speed = speed
    else:
        speed = 100 - speed
    pwm.ChangeDutyCycle(speed)


def button_1_pressed():
    global speed, count
    count += 1
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control(speed, 0)


def button_2_pressed():
    global speed, count_1
    count_1 += 1
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control(speed, 1)


def main():
    lcd_init()
    pull_up_bts()
    motor_control(0, 0)
    global speed
    while True:
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            speed = 0
            while True:
                if GPIO.input(BTS['BT_1']) == GPIO.LOW:
                    button_1_pressed()
                    lcd_display_string("Quay tien ", 1)
                    lcd_display_string(f"Speed: {speed}", 2)
                    time.sleep(0.1)
                else:
                    for new_speed in range(speed, -1, -10):
                        motor_control(new_speed, 0)
                        lcd_display_string("Giam toc ", 1)
                        lcd_display_string(f"Speed: {new_speed}", 2)
                        time.sleep(0.25)
                        if GPIO.input(BTS['BT_3']) == GPIO.LOW:
                            motor_control(0, 0)
                            lcd_display_string("Stop ", 1)
                            lcd_display_string("Speed: {0}", 2)
                            break
                    break
        if GPIO.input(BTS['BT_2']) == GPIO.LOW:
            speed = 0
            while True:
                if GPIO.input(BTS['BT_2']) == GPIO.LOW:
                    button_2_pressed()
                    lcd_display_string("Quay lui ", 1)
                    lcd_display_string(f"Speed: {speed}", 2)
                    time.sleep(0.1)
                elif GPIO.input(BTS['BT_3']) == GPIO.LOW:
                    motor_control(0, 1)
                    lcd_display_string("Stop ", 1)
                    lcd_display_string("Speed: {0}", 2)
                    break
                else:
                    for new_speed in range(speed, -1, -10):
                        motor_control(new_speed, 1)
                        lcd_display_string("Giam toc ", 1)
                        lcd_display_string(f"Speed: {new_speed}", 2)
                        time.sleep(0.25)
                        if GPIO.input(BTS['BT_3']) == GPIO.LOW:
                            motor_control(0, 0)
                            lcd_display_string("Stop ", 1)
                            lcd_display_string("Speed: {0}", 2)
                            break
                    break


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
    lcd_clear()
