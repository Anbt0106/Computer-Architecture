import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LCD = 2
LED = 13

GPIO.setup(LCD, GPIO.OUT)
GPIO.setup(LED, GPIO.OUT)

# Nếu LCD bật thì LED tắt và ngược lại. Sau 4 lần cả LCD và LED đều tắt.
def main():
    for i in range(4):
        GPIO.output(LCD, True)
        GPIO.output(LED, False)
        time.sleep(1)
        GPIO.output(LCD, False)
        GPIO.output(LED, True)
        time.sleep(1)
    GPIO.output(LCD, False)
    GPIO.output(LED, False)


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
