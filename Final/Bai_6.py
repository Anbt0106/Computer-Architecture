import RPi.GPIO as GPIO
import time

# Khai báo chân GPIO
DHT11_PIN = 7
RELAY_1 = 16
RELAY_2 = 12
BUTTON_1 = 21
BUTTON_2 = 26
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.005
E_DELAY = 0.005
ROOM_TEMPERATURE_THRESHOLD = 25
ROOM_HUMIDITY_THRESHOLD = 80

# Biến toàn cục
people_count = 0

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DHT11_PIN, GPIO.IN)
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)

GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for pin in LCD_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

# Đọc dữ liệu từ cảm biến DHT11
def read_dht11():
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
        humidity += humidity_bit[i] * 2**(7-i)
        humidity_point += humidity_point_bit[i] * 2**(7-i)
        temperature += temperature_bit[i] * 2**(7-i)
        temperature_point += temperature_point_bit[i] * 2**(7-i)
        checksum += check_bit[i] * 2**(7-i)
        check = humidity + humidity_point + temperature + temperature_point
    if checksum ==check:
        return temperature + temperature_point, humidity + humidity_point
    else:
        return None, None

# Điều khiển LCD
def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def lcd_init():
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

# Điều khiển rơ-le
def control_relay(temperature, humidity):
    if temperature < ROOM_TEMPERATURE_THRESHOLD or humidity < ROOM_HUMIDITY_THRESHOLD:
        GPIO.output(RELAY_1, GPIO.HIGH)
        GPIO.output(RELAY_2, GPIO.LOW)
    else:
        GPIO.output(RELAY_1, GPIO.LOW)
        GPIO.output(RELAY_2, GPIO.HIGH)

# Xử lý nút bấm
def handle_buttons():
    global people_count
    if GPIO.input(BUTTON_1) == GPIO.LOW:
        people_count += 1
        time.sleep(0.3)
    if GPIO.input(BUTTON_2) == GPIO.LOW and people_count > 0:
        people_count -= 1
        time.sleep(0.3)

# Chương trình chính
def main():
    global people_count
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    while True:
        handle_buttons()
        if people_count > 0:
            temperature, humidity = read_dht11()
            if temperature is not None and humidity is not None:
                control_relay(temperature, humidity)
                lcd_display_string(f"Ppl: {people_count}", 1)
                lcd_display_string(f"T: {temperature}C H: {humidity}%", 2)
            else:
                lcd_display_string("Sensor Error", 2)
                lcd_display_string(f"Ppl: {people_count}", 1)
        else:
            GPIO.output(RELAY_1, GPIO.LOW)
            GPIO.output(RELAY_2, GPIO.LOW)
            lcd_display_string("Room Empty", 1)
            lcd_display_string("", 2)
        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    lcd_clear()
