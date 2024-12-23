import Rpi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LED = 13
LCD = 2

GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LCD, GPIO.OUT)


def main():
    while True:
        GPIO.output(LCD, not GPIO.input(LCD))
        GPIO.output(LED, not GPIO.input(LED))
        time.sleep(1)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
