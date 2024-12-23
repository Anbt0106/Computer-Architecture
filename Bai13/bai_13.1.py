import cv2
import RPi.GPIO as GPIO
import time


def main():
    BT1 = 21
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    global nameWindow
    nameWindow = "Camera User"
    capture = cv2.VideoCapture(0)
    print("Capture ready")
    while True:
        ret, frame = capture.read()
        if GPIO.input(BT1) == GPIO.LOW:
            while True:
                cv2.imshow("Picture camera", frame)
                cv2.waitKey()
                cv2.destroyWindow("Picture camera")
            break


try:
    main()
except KeyboardInterrupt:
    cv2.destroyWindow(nameWindow)
    GPIO.cleanup()
