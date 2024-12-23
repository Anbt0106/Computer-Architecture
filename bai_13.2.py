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
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640, 480))
    cap_video = False
    while True:
        ret, frame = capture.read()
        if GPIO.input(BT1) == GPIO.LOW:
            print("Press BT1")
            cv2.imshow(nameWindow, frame)
            out.write(frame)
            print("Save video")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                GPIO.cleanup()
                cv2.destroyWindow(nameWindow)
                break
            continue
        if cap_video:
            cv2.imshow(nameWindow, frame)
            out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            GPIO.cleanup()
            cv2.destroyWindow(nameWindow)
            break


try:
    main()
except KeyboardInterrupt:
    cv2.destroyWindow(nameWindow)
    GPIO.cleanup()
