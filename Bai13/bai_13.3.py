import cv2
import RPi.GPIO as GPIO
import time


def main():
    BT1 = 21
    GPIO.setmode(GPIO.BCM)
    # GPIO.setwarnings(False)
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    global nameWindow
    nameWindow = "Camera User"
    capture = cv2.VideoCapture(0)
    print("Capture ready")
    out = cv2.VideoWriter('output.avi', fourcc=cv2.VideoWriter_fourcc(*'MJPG'), fps=20.0, frameSize=(640, 480))
    cap_video = False
    button_pressed = False

    while True:
        ret, frame = capture.read()
        button_state = GPIO.input(BT1)
        if button_state == GPIO.LOW and not button_pressed:
            button_pressed = True
            cap_video = not cap_video
            if not cap_video:
                cv2.destroyWindow(nameWindow)
            time.sleep(0.5)
        elif button_state == GPIO.HIGH:
            button_pressed = False
        if cap_video:
            cv2.imshow(nameWindow, frame)
            out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    capture.release()
    out.release()
    GPIO.cleanup()
    cv2.destroyAllWindows()


try:
    main()
except KeyboardInterrupt:
    cv2.destroyWindow(nameWindow)
    GPIO.cleanup()
