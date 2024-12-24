import RPi.GPIO as GPIO
import time

# GPIO Pin Configurations
BUTTON_PIN = 21
RELAY_PIN = 16

# LCD Pin Configurations
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
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
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# LCD Functions
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

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

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

# Button Reading Function
def read_button():
    return GPIO.input(BUTTON_PIN) == GPIO.LOW

# Password Entry Logic
def main():
    lcd_init()
    lcd_clear()
    lcd_display_string("Enter Password:", 1)
    password = ""
    options = [str(i) for i in range(10)]
    index = 0

    while True:
        if read_button():  # Button pressed
            #start_time = time.time()
            #while not read_button():
                #pass
            lcd_clear()
            while read_button():
                #if time.time() - start_time > 1:  # Scroll through options
                lcd_display_string("Select: " + options[index], 1)
                index = (index + 1) % len(options)
                time.sleep(0.5)  # Debounce delay

            # Button released, confirm selection
            if index < 0:
                index = 0
            else:
                index = index - 1
            selected_digit = options[index]
            password += selected_digit
            lcd_display_string("Selected: " + selected_digit, 2)
            time.sleep(3)  # Display the selected digit for 3 second

            # Mask with "*"
            masked_password = "*" * len(password)
            lcd_clear()
            lcd_display_string(masked_password, 2)

            # Check if password is "999"
            if password == "999":
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Activate relay
                lcd_clear()
                lcd_display_string("Success!", 1)
                lcd_display_string("Access Granted", 2)
                time.sleep(5)
                # loop back
                GPIO.output(RELAY_PIN, GPIO.LOW)
                lcd_clear()
                lcd_display_string("Enter Password:", 1)
                password = ""
            elif len(password) >= 3:  # Clear input if incorrect
                lcd_clear()
                lcd_display_string("Wrong Password!", 1)
                time.sleep(2)
                lcd_clear()
                lcd_display_string("Enter Password:", 1)
                password = ""
        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
