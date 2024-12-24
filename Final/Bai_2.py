import RPi.GPIO as GPIO
import time

# Pin configuration
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
BT1 = 21
message = "Hello-World"

# Initialize LCD
def lcd_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)

# Clear the LCD
def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

# Send a byte to the LCD
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

# Display a string on the LCD
def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def animate_character_left_to_right(char, target_pos, line, buffer):
    for pos in range(-1, target_pos + 1):
        if not GPIO.input(BT1):  # Check for button press
            return True  # Stop animation if button is pressed
        lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
        display_line = buffer[:]
        if 0 <= pos < LCD_WIDTH:
            display_line[pos] = char
        lcd_display_string("".join(display_line), line)
        time.sleep(0.09)
    buffer[target_pos] = char
    return False

def animate_character_right_to_left(char, target_pos, line, buffer):
    for pos in range(LCD_WIDTH, target_pos, -1):
        if not GPIO.input(BT1):  # Check for button press
            return True  # Stop animation if button is pressed
        lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
        display_line = buffer[:]
        if 0 <= pos - 1 < LCD_WIDTH:
            display_line[pos - 1] = char
        lcd_display_string("".join(display_line), line)
        time.sleep(0.09)
    buffer[target_pos] = char
    return False


def button_task():
    lcd_init()
    lcd_clear()
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    press_count = 0
    buffer = [" "] * LCD_WIDTH
    animation_done = False  # To track if the animation has completed

    while True:
        if not GPIO.input(BT1):  # Button pressed
            press_count = (press_count + 1) % 3  # Cycle through tasks
            time.sleep(0.2)  # Debounce delay
            lcd_clear()
            buffer = [" "] * LCD_WIDTH
            animation_done = False  # Reset animation state

        if press_count == 2:
            # Task 2: Right to left animation
            if not animation_done:
                for i in range(len(message)):  # Start with first character
                    if animate_character_right_to_left(message[i], i, 1, buffer):
                        break  # Stop animation if button is pressed
                animation_done = True  # Mark animation as completed
            time.sleep(0.1)
        elif   press_count == 1:
            # Task 1: Left to right animation
            if not animation_done:
                for i in range(len(message) - 1, -1, -1):  # Start with last character
                    if animate_character_left_to_right(message[i], i + (LCD_WIDTH - len(message)), 1, buffer):
                        break  # Stop animation if button is pressed
                animation_done = True  # Mark animation as completed
            time.sleep(0.1)
        elif press_count == 3:
            # Task 3: Clear screen
            lcd_clear()
            press_count=0
            animation_done = False  # Reset animation state
            time.sleep(0.1)

# Main function
def main():
    try:
        button_task()
    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()

# Run the program
if __name__ == "__main__":
    main()

