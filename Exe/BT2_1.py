import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LCD = 2
GPIO.setup(LCD, GPIO.OUT)


def main():
    while True:
        GPIO.output(LCD, not GPIO.input(LCD))
        time.sleep(1)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
