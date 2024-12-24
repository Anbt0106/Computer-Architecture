import cv2
import RPi.GPIO as GPIO
import numpy as np
import time

# GPIO setup
RELAY_1 = 16
RELAY_2 = 12
BT1 = 21
BT2 = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Function to control relays
def activate_relay(relay_pin, state):
    GPIO.output(relay_pin, GPIO.HIGH if state else GPIO.LOW)


# Function to capture an image
def capture_image():
    name_window = "Camera User"
    capture = cv2.VideoCapture(0)
    ret, frame = capture.read()
    capture.release()
    if ret:
        cv2.imshow(name_window, frame)
        cv2.waitKey(2000)  # Display the image for 2 seconds
        cv2.destroyWindow(name_window)
    return frame


# Function to process the image and count pixels
def count_color_pixels(image, lower_bound, upper_bound):
    hsv_frame = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    return cv2.countNonZero(mask)


# Main logic
try:
    print("System Ready")
    while True:
        if GPIO.input(BT1) == GPIO.LOW:  # Capture image when BT1 is pressed
            print("Capturing Image...")
            image = capture_image()
            if image is not None:
                print("Image Captured. Processing...")

                # Define HSV ranges for red and green
                lower_red = np.array([0, 120, 70])
                upper_red = np.array([10, 255, 255])
                lower_green = np.array([35, 100, 100])
                upper_green = np.array([85, 255, 255])

                # Count pixels for red and green
                red_count = count_color_pixels(image, lower_red, upper_red)
                green_count = count_color_pixels(image, lower_green, upper_green)

                print(f"Red Pixels: {red_count}, Green Pixels: {green_count}")

                # Compare and activate relays based on counts
                if red_count > green_count:
                    print("Red dominates. Activating Relay 1.")
                    activate_relay(RELAY_1, True)
                    time.sleep(1)
                    activate_relay(RELAY_1, False)
                else:
                    print("Green dominates. Activating Relay 2.")
                    activate_relay(RELAY_2, True)
                    time.sleep(1)
                    activate_relay(RELAY_2, False)

        time.sleep(0.1)  # Prevent excessive polling

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
    cv2.destroyAllWindows()
