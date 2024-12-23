import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 13
LCD = 2
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LCD, GPIO.OUT)


def tongleLED_LCD():
    GPIO.output(LCD, not GPIO.input(LCD))
    GPIO.output(LED, not GPIO.input(LED))


try:
    while True:
        tongleLED_LCD()
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
