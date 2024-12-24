import cv2
import RPi.GPIO as GPIO
import time
import numpy as np

# GPIO pin configuration
BT1 = 21  # Button 1
BT2 = 26  # Button 2
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Initialize GPIO and LCD
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

# Capture image function
def capture_image():
    capture = cv2.VideoCapture(0)
    ret, frame = capture.read()
    capture.release()
    if ret:
        cv2.imshow("Ảnh chụp camera", frame)
        cv2.waitKey(2000)  # Display the image for 2 seconds
        cv2.destroyAllWindows()
    return frame if ret else None

# Count red pixels in an image
def count_red_pixels(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    red_pixel_count = cv2.countNonZero(red_mask)
    return red_pixel_count

# Main logic
def main():
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    lcd_init()
    lcd_clear()
    lcd_display_string("System Ready", 1)
    captured_image = None

    try:
        while True:
            if GPIO.input(BT1) == GPIO.LOW:  # Capture image
                lcd_clear()
                lcd_display_string("Capturing...", 1)
                print("Capturing image...")
                captured_image = capture_image()
                if captured_image is not None:
                    lcd_clear()
                    lcd_display_string("Image Captured!", 1)
                    print("Image captured successfully.")
                else:
                    lcd_clear()
                    lcd_display_string("Capture Failed!", 1)
                    print("Failed to capture image.")

            if GPIO.input(BT2) == GPIO.LOW and captured_image is not None:  # Count red pixels
                lcd_clear()
                lcd_display_string("Processing...", 1)
                print("Processing image...")
                red_pixel_count = count_red_pixels(captured_image)
                lcd_clear()
                message = f"Red Pixels: {red_pixel_count}"
                print(message)
                lcd_display_string("Red Pixels:", 1)
                lcd_display_string(str(red_pixel_count), 2)
                time.sleep(3)  # Display result for 3 seconds
                lcd_clear()
                lcd_display_string("System Ready", 1)

            time.sleep(0.1)  # Small delay to prevent button bouncing

    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()
        cv2.destroyAllWindows()
        print("System exited.")

# Run the program
if __name__ == "__main__":
    main()
