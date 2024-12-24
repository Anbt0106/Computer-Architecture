import RPi.GPIO as GPIO
import time

# GPIO Pin Configurations
BUTTON_BACK = 21  # Back button
BUTTON_UP = 26    # Up button
BUTTON_DOWN = 20  # Down button
BUTTON_SELECT = 19  # Select button
RELAY_1 = 16
RELAY_2 = 12
LED_PIN = 13

# LCD Pin Configurations
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

# Menu Data
MENU = {
    "Main Menu": ["Menu 1", "Menu 2"],
    "Menu 1": ["Menu 1_1"],
    "Menu 2": ["Menu 2_2"],
    "Menu 1_1": ["LED Control"],
    "Menu 2_2": ["Relay 1", "Relay 2"]
}
ACTIONS = {
    "LED Control": lambda: GPIO.output(LED_PIN, not GPIO.input(LED_PIN)),
    "Relay 1": lambda: GPIO.output(RELAY_1, not GPIO.input(RELAY_1)),
    "Relay 2": lambda: GPIO.output(RELAY_2, not GPIO.input(RELAY_2)),
}

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_BACK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_SELECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

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
    for char in message.ljust(LCD_WIDTH)[:LCD_WIDTH]:
        lcd_byte(ord(char), LCD_CHR)

# Button Handling
def read_button(pin):
    return GPIO.input(pin) == GPIO.LOW

# Menu Navigation Logic
def menu_navigation():
    current_menu = "Main Menu"
    current_index = 0
    menu_stack = []

    while True:
        options = MENU.get(current_menu, [])
        selected_option = options[current_index] if options else current_menu

        # Display current menu or action
        lcd_display_string(current_menu, 1)
        lcd_display_string(selected_option, 2)

        # Button Actions
        if read_button(BUTTON_BACK):  # Back
            if menu_stack:
                current_menu = menu_stack.pop()
                current_index = 0
            time.sleep(0.3)
            lcd_clear()

        elif read_button(BUTTON_UP):  # Up
            current_index = (current_index - 1) % len(options) if options else 0
            time.sleep(0.3)
            lcd_clear()

        elif read_button(BUTTON_DOWN):  # Down
            current_index = (current_index + 1) % len(options) if options else 0
            time.sleep(0.3)
            lcd_clear()

        elif read_button(BUTTON_SELECT):  # Select
            if selected_option in MENU:  # Navigate deeper
                menu_stack.append(current_menu)
                current_menu = selected_option
                current_index = 0
                lcd_clear()
            elif selected_option in ACTIONS:  # Perform action
                lcd_clear()
                lcd_display_string(f"{selected_option}...", 1)
                ACTIONS[selected_option]()
                time.sleep(2)  # Pause for user feedback
            time.sleep(0.3)

try:
    lcd_init()
    lcd_clear()
    menu_navigation()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
