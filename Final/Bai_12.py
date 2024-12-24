import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
TRIG = 15
ECHO = 4
PWM_PIN = 24
DIR_PIN = 25
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}

# LCD Constants
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

# Water Level Thresholds (in cm)
MAX_DISTANCE = 50  # Distance from the sensor to the minimum water level
MIN_DISTANCE = 10  # Distance from the sensor to the maximum water level

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Ultrasonic Sensor Pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Motor Control Pins
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

# PWM Setup for Motor
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

# LCD Initialization
for pin in LCD_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

# Ultrasonic Sensor Function
def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Convert to cm
    return round(distance, 2)

# Motor Control Function
def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)

# Main Function
def main():
    lcd_init()
    lcd_clear()
    GPIO.output(TRIG, False)
    time.sleep(2)

    try:
        while True:
            # Measure distance
            distance = get_distance()

            # Display distance on LCD
            lcd_clear()
            lcd_display_string(f"Dist: {distance} cm", 1)

            if distance > MAX_DISTANCE:
                # If water level is below minimum, turn on the pump
                motor_control(50, 1)  # 50% speed, forward
                lcd_display_string("Status: Pump ON", 2)

            #elif distance < MIN_DISTANCE:
                # If water level is above maximum, turn off the pump
             #   motor_control(0, 0)  # Stop motor
              #  lcd_display_string("Status: Pump OFF", 2)

            else:
                # Maintain water level (Pump OFF)
                motor_control(0, 0)  # Stop motor
                lcd_display_string("Status: Stable", 2)

            time.sleep(1)

    except KeyboardInterrupt:
        # Cleanup on exit
        lcd_clear()
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
