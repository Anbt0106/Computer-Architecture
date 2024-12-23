# chua run

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
BT_1 = 21

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)


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


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def show_left2right(message):
    global button_state
    message_list = list(message)
    new_message = ""
    while len(message_list) > 0:
        char = message_list.pop(0)
        length_loop = LCD_WIDTH - len(new_message) - 1
        for i in range(length_loop):
            lcd_clear()
            lcd_display_string(" " * i + char + " " * (length_loop - i) + new_message, 1)
            time.sleep(0.1)
            if GPIO.input(BT_1) == GPIO.LOW:
                button_state = (button_state + 1)
                time.sleep(0.2)
                return
        new_message += char


def show_right2left(message):
    global button_state
    message_list = list(message)
    new_message = ""
    while len(message_list) > 0:
        char = message_list.pop(0)
        length_loop = LCD_WIDTH - len(new_message) - 1
        for i in range(length_loop):
            lcd_clear()
            lcd_display_string(new_message + " " * i + char, 1)
            time.sleep(0.1)
            if GPIO.input(BT_1) == GPIO.LOW:
                button_state = (button_state + 1)
                time.sleep(0.2)
                return
        new_message += char


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    global button_state
    button_state = 0
    message = "Hello World!"
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            button_state = (button_state + 1)
            time.sleep(0.25)
        if button_state == 1:
            show_left2right("Hello World!")
        elif button_state == 2:
            show_right2left("Hello World!")
        else:
            lcd_clear()
            time.sleep(0.1)
            button_state = 0


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
