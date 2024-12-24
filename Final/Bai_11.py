import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
SERVO = 6
BT1 = 21
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}

# LCD Constants
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Button Configuration
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Servo Configuration
GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)
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

# Servo Motor Function
def set_servo_angle(angle):
    duty = angle / 18
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)


# Main Logic
def main():
    lcd_init()
    lcd_clear()
    #GPIO.output(SERVO, False)
    time.sleep(2)

    current_angle = 0  # Start angle

    try:
        while True:
            # Check button press
            if GPIO.input(BT1) == GPIO.LOW:
                # Update angle
                current_angle += 10
                if current_angle > 160:
                    current_angle = 0

                # Move servo and update LCD
                set_servo_angle(current_angle)
                lcd_clear()
                lcd_display_string(f"Angle: {current_angle}", 1)
                time.sleep(0.5)  # Debounce delay

    except KeyboardInterrupt:
        # Cleanup on exit
        lcd_clear()
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
