import RPi.GPIO as GPIO
import time

from multiprocessing import Process, Value, Array
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import spidev

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}  # LCD PINS
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

BTS = {'BT_1': 21, 'BT_2': 26, 'BT_3': 20, 'BT_4': 19}

SERVO_PIN = 6
up = True
firstRequest = True

DIR_PIN = 25
PWM_PIN = 24

rl_1 = 16
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10000000
spi.mode = 0x00

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(rl_1, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)
pwm_dc = GPIO.PWM(PWM_PIN, 100)
pwm_dc.start(0)


def pull_up_bts():
    for pin in BTS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def set_servo_angle(angle):
    duty = angle / 18 + 2
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    servo_pwm.ChangeDutyCycle(0)


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)
    GPIO.output(LCD_PINS['BL'], True)


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


def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    if direction == 0:  # nếu direction = 0 thì speed = speed
        speed = speed
    else:  # nếu direction = 1 thì speed = 100 - speed
        speed = 100 - speed
    pwm_dc.ChangeDutyCycle(speed)  # thay đổi duty cycle của pwm


motor_control(0, 0)


def max7219_write(register, data):
    spi.xfer2([register, data])


def max7219_init():
    max7219_write(0x0C, 0x01)  # Normal operation
    max7219_write(0x0B, 0x07)  # Scan limit: 8 digits
    max7219_write(0x09, 0x00)  # Decode mode: No decode
    max7219_write(0x0A, 0x00)  # Intensity: 1/32
    max7219_write(0x0F, 0x00)  # Display test: Normal operation


def create_text_image(text, width, height):
    image = Image.new('1', (width, height), 0)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    font_size = 1
    text_position = (1, -1)
    draw.text(text_position, text, font=font, fill=1)
    return image


def display_image(image):
    pixels = np.array(image)
    for y in range(8):
        row_data = 0
        for x in range(8):
            if pixels[y, x]:
                row_data |= 1 << x
        max7219_write(y + 1, row_data)


def clear_matrix():
    max7219_write(0x0c, 0x00)


def demo(currentLevel, opened):
    max7219_init()
    while 1:
        width, height = 8, 8
        text = str(int(currentLevel.value) + 1)
        image = create_text_image(text, width, height)
        flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)
        display_image(flipped_image)
        time.sleep(0.1)
        if opened.value:
            time.sleep(0.3)


def led(currentLevel, opened):
    try:
        demo(currentLevel, opened)
    except KeyboardInterrupt:
        pass


def show_screen(order, opened):
    lcd_init()
    lcd_clear()
    time.sleep(0.5)
    while 1:
        if opened.value:
            lcd_display_string("Door opened", 1)
        else:
            lcd_display_string("Door closed", 1)

    ordered = ""
    for i in range(len(order)):
        if order[i]:
            ordered += str(i + 1) + " "
        else:
            ordered += "  "
    lcd_display_string(f"Order: {ordered}", 2)
    time.sleep(0.5)


def quay_DC():
    motor_control(100, 1)
    time.sleep(2)


def quay_nguoc_DC():
    motor_control(100, 0)
    time.sleep(2)


def dung_DC():
    motor_control(0, 0)
    time.sleep(2)


def thang_may(order, currentLevel, opened):
    global up, firstRequest

    for i in range(4):
        if order[i]:
            break
        if i == 3:
            return

    if up:
        for i in range(int(currentLevel.value), 4):
            if i == 3 and order[i] == 0:
                up = False
            elif order[i]:
                break

    if not up:
        for i in range(int(currentLevel.value), -1, -1):
            if i == 0 and order[i] == 0:
                up = True
                return
            elif order[i]:
                break

    if firstRequest:
        set_servo_angle(60)
        opened.value = True
        GPIO.output(rl_1, GPIO.HIGH)
        time.sleep(1)
        set_servo_angle(120)
        opened.value = False
        GPIO.output(rl_1, GPIO.LOW)
        time.sleep(1)

    if up:
        quay_DC()
    else:
        quay_nguoc_DC()
    while (order[int(currentLevel.value)] == False):
        if up:
            currentLevel.value += 1
        else:
            currentLevel.value -= 1
        time.sleep(2)

    order[int(currentLevel.value)] = False
    dung_DC()
    set_servo_angle(60)
    opened.value = True
    GPIO.output(rl_1, GPIO.HIGH)
    time.sleep(1)
    set_servo_angle(120)
    opened.value = False
    GPIO.output(rl_1, GPIO.LOW)
    time.sleep(1)
    firstRequest = True

    for i in order:
        if i == 1:
            firstRequest = False


def read(order, BT1, BT2, BT3, BT4):
    while 1:
        if GPIO.input(BT1) == GPIO.LOW:
            order[0] = 1
        if GPIO.input(BT2) == GPIO.LOW:
            order[1] = 1
        if GPIO.input(BT3) == GPIO.LOW:
            order[2] = 1
        if GPIO.input(BT4) == GPIO.LOW:
            order[3] = 1
        time.sleep(0.2)


def main(order, currentLevel, opened):
    pull_up_bts()
    Process(target=read, args=(order, *BTS.values())).start()
    Process(target=led, args=(currentLevel, opened)).start()
    Process(target=show_screen, args=(order, opened)).start()
    while 1:
        thang_may(order, currentLevel, opened)
        time.sleep(0.3)


if __name__ == '__main__':
    try:
        currentLevel = Value('d', 0)
        order = Array('i', [0 for _ in range(4)])
        opened = Value('i', False)
        main(order, currentLevel, opened)
    except KeyboardInterrupt:
        GPIO.cleanup()
