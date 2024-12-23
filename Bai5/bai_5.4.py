import RPi.GPIO as GPIO
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS = {"BT_1": 21, "BT_2": 26}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def pull_up_bts():
    for pin in BTS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005  # để chính xác 0.0005 để tránh lỗi trễ khi gửi tín hiệu điều khiển đến LCD
E_DELAY = 0.0005
RELAY_1 = 12

GPIO.setup(RELAY_1, GPIO.OUT)


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


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


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def main():
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    pull_up_bts()
    dem = 0
    people_inside = 0
    while True:
        if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
            time.sleep(0.25)
            while True:
                if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
                    people_inside += 1
                    time.sleep(0.25)
                    lcd_display_string(f"Person: {people_inside}", 1)
                    break
        if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
            time.sleep(0.25)
            while True:
                if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
                    people_inside -= 1
                    if people_inside < 0:
                        people_inside = 0
                    time.sleep(0.25)
                    lcd_display_string(f"Person: {people_inside}", 1)
                    break
        if people_inside > 0:
            GPIO.output(RELAY_1, GPIO.HIGH)
        else:
            GPIO.output(RELAY_1, GPIO.LOW)


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
