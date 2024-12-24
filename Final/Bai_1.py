import RPi.GPIO as GPIO
import time

# GPIO Pin Configurations
BUTTON_1 = 21
BUTTON_2 = 26
BUTTON_3 = 20
BUTTON_4 = 19
LED_PIN = 13  # LED pin
LCD_BACKLIGHT = 2  # LCD Backlight pin

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(LCD_BACKLIGHT, GPIO.OUT)

# LED and Backlight State
LED_STATE = False
LCD_BACKLIGHT_STATE = False

# Button Press Tracking
button_1_pressed = False
button_3_pressed = False

def read_button(pin):
    return GPIO.input(pin) == GPIO.LOW

try:
    while True:
        # Check for Button 1 followed by Button 2
        if read_button(BUTTON_1):
            button_1_pressed = True
            time.sleep(0.2)  # Debounce
        if button_1_pressed and read_button(BUTTON_2):
            GPIO.output(LED_PIN, True)
            LED_STATE = True
            button_1_pressed = False  # Reset state
            time.sleep(0.2)  # Debounce

        # Check for Button 3 followed by Button 4
        if read_button(BUTTON_3):
            button_3_pressed = True
            time.sleep(0.2)  # Debounce
        if button_3_pressed and read_button(BUTTON_4):
            GPIO.output(LCD_BACKLIGHT, True)
            LCD_BACKLIGHT_STATE = True
            button_3_pressed = False  # Reset state
            time.sleep(0.2)  # Debounce

        # Check for simultaneous press of Button 1 and Button 3
        if read_button(BUTTON_1) and read_button(BUTTON_3):
            GPIO.output(LED_PIN, False)
            GPIO.output(LCD_BACKLIGHT, False)
            LED_STATE = False
            LCD_BACKLIGHT_STATE = False
            time.sleep(0.5)  # Prevent multiple triggers
        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()