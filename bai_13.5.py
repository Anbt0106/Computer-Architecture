import cv2
import copy
import RPi.GPIO as GPIO


def main():
    BT1 = 21
    BT2 = 26
    cap = cv2.VideoCapture(0)
    print("Capture ready")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    isdraw = False
    while True:
        if GPIO.input(BT1) == GPIO.LOW:
            print("Press BT1")
            while True:
                ret, src = cap.read()
                frame = copy.copy(src)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, (0, 118, 130), (5, 255, 255))
                _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                result = cv2.bitwise_and(frame, frame, mask=mask)
                if GPIO.input(BT2) == GPIO.LOW:
                    print("Press BT2")
                    isdraw = not isdraw
                if isdraw:
                    draw(contours, result)
                cv2.imshow("Image", result)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    GPIO.cleanup()
                    cv2.destroyAllWindows()
                    break


def draw(contours, result):
    if contours is None:
        print("Don't find contours")
    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) > 300:
            hull = cv2.convexHull(contours[i])
            cv2.drawContours(result, [hull], -1, (0, 0, 255), 3)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    cv2.destroyAllWindows()
