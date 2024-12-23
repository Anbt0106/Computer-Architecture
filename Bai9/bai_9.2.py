import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LIGHT_SS = 5
GPIO.setup(LIGHT_SS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# RELAY_1 = 12
# RELAY_2 = 16
# LED = 13
# GPIO.setup(RELAY_1, GPIO.OUT)
# GPIO.setup(RELAY_2, GPIO.OUT)
# GPIO.setup(LED, GPIO.OUT)

RLS = {"RELAY_1": 12, "RELAY_2": 16, "LED": 13}
for pin in RLS.values():
    GPIO.setup(pin, GPIO.OUT)

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005


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
    time.sleep(0.5)
    GPIO.output(LCD_PINS['BL'], True)
    while True:
        if GPIO.input(LIGHT_SS) == 0:
            lcd_clear()
            GPIO.output(RLS['RELAY_1'], GPIO.LOW)
            GPIO.output(RLS['RELAY_1'], GPIO.LOW)
            lcd_display_string('Light', 1)
            lcd_display_string('Relay: off', 2)
        else:
            lcd_clear()
            GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
            lcd_display_string('Dark', 1)
            lcd_display_string('Relay 1 on ', 2)
            time.sleep(3)
            GPIO.output(RLS['RELAY_1'], GPIO.LOW)
            GPIO.output(RLS['RELAY_2'], GPIO.HIGH)
            lcd_display_string('Relay 2 on after 3s', 2)
        time.sleep(1)


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
