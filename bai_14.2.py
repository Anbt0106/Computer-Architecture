import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Array

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS = {"BT1": 21, "BT2": 26, "BT3": 20, "BT4": 19}
RELAYS = {"RELAY_1": 12, "RELAY_2": 16}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
DHT11_PIN = 7
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


def read_dht11():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DHT11_PIN, GPIO.OUT)
    GPIO.output(DHT11_PIN, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(DHT11_PIN, GPIO.HIGH)
    GPIO.setup(DHT11_PIN, GPIO.IN)
    while GPIO.input(DHT11_PIN) == GPIO.LOW:
        pass
    while GPIO.input(DHT11_PIN) == GPIO.HIGH:
        pass
    data = []
    for i in range(40):
        while GPIO.input(DHT11_PIN) == GPIO.LOW:
            pass
        count = 0
        while GPIO.input(DHT11_PIN) == GPIO.HIGH:
            count += 1
            if count > 100:
                break
        if count > 8:
            data.append(1)
        else:
            data.append(0)
    humidity_bit = data[0:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    checksum = 0
    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7 - i)
        humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
        temperature += temperature_bit[i] * 2 ** (7 - i)
        temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
        checksum += check_bit[i] * 2 ** (7 - i)
    check = humidity + humidity_point + temperature + temperature_point
    if checksum == check:
        return temperature + temperature_point, humidity + humidity_point
    else:
        return None, None


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


def show_screen(t_h, t_h_setting):
    lcd_init()
    time.sleep(1)
    lcd_clear()
    GPIO.output(LCD_PINS['BL'], True)
    time.sleep(1)
    while 1:
        temperature, humidity = list(t_h)
        temperature_setting, humidity_setting = list(t_h_setting)
        lcd_display_string('temp: {}*C ||{}'.format(temperature, temperature_setting), 1)
        lcd_display_string('humid: {}% || {}'.format(humidity, humidity_setting), 2)
        time.sleep(0.5)


def read_bts(t_h_setting, *args):
    def pull_up_bts():
        for pin in BTS.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pull_up_bts()
    while 1:
        if GPIO.input(BTS['BT1']) == 0:
            t_h_setting[0] -= 1
        if GPIO.input(BTS['BT2']) == 0:
            t_h_setting[0] += 1
        if GPIO.input(BTS['BT3']) == 0:
            t_h_setting[1] -= 1
        if GPIO.input(BTS['BT4']) == 0:
            t_h_setting[1] += 1
        time.sleep(0.2)


def control_relays(t_h, t_h_setting):
    def relays_init():
        for pin in RELAYS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    relays_init()
    while 1:
        temperature, humidity = list(t_h)
        temperature_setting, humidity_setting = list(t_h_setting)
        if temperature > temperature_setting:
            GPIO.output(RELAYS['RELAY_1'], GPIO.HIGH)
        else:
            GPIO.output(RELAYS['RELAY_1'], GPIO.LOW)
        if humidity > humidity_setting:
            GPIO.output(RELAYS['RELAY_2'], GPIO.HIGH)
        else:
            GPIO.output(RELAYS['RELAY_2'], GPIO.LOW)
        time.sleep(1)


def main(t_h, t_h_setting):
    Process(target=read_bts, args=(t_h_setting,)).start()
    Process(target=control_relays, args=(t_h, t_h_setting)).start()
    Process(target=show_screen, args=(t_h, t_h_setting)).start()
    while 1:
        temperature, humidity = read_dht11()
        if humidity is not None and temperature is not None:
            t_h[:] = [temperature, humidity]
        time.sleep(1)


if __name__ == "__main__":
    try:
        t_h = Array('i', [0, 0])
        t_h_setting = Array('i', [20, 20])
        main(t_h, t_h_setting)
    except KeyboardInterrupt:
        GPIO.cleanup()

