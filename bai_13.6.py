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
                green_mask = cv2.inRange(hsv, (35, 89, 107), (45, 241, 213))
                _, contoyrsGreen, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                red_mask = cv2.inRange(hsv, (0, 118, 130), (5, 255, 255))
                _, contoursRed, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                group = green_mask + red_mask
                group = group >= 1
                group = group.astype('unit8') * 255
                result = cv2.bitwise_and(frame, frame, mask=group)
                if GPIO.input(BT2) == GPIO.LOW:
                    print("Press BT2")
                    isdraw = True
                if isdraw:
                    draw(contoursRed, contoyrsGreen, result)
                cv2.imshow("Threshold", result)
                cv2.imshow("Camera", src)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    GPIO.cleanup()
                    cv2.destroyAllWindows()
                    break


def draw(contoursRed, contoyrsGreen, frame):
    for i in range(len(contoursRed)):
        if cv2.contourArea(contoursRed[i]) > 300:
            hull = cv2.convexHull(contoursRed[i])
            cv2.drawContours(frame, [hull], -1, (0, 0, 255), 3)

    for i in range(len(contoyrsGreen)):
        if cv2.contourArea(contoyrsGreen[i]) > 300:
            hull = cv2.convexHull(contoyrsGreen[i])
            cv2.drawContours(frame, [hull], -1, (0, 255, 0), 3)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    cv2.destroyAllWindows()
