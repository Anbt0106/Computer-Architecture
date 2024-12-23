import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LED = 13
GPIO.setup(LED, GPIO.OUT)

count = 0


def main():
    global count
    while True:
        GPIO.output(LED, GPIO.HIGH)  # Turn on LED
        count += 1
        print("LED on: ", count)
        time.sleep(1)
        GPIO.output(LED, GPIO.LOW)  # Turn off LED
        time.sleep(1)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
