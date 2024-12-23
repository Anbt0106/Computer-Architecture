import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 13
GPIO.setup(LED, GPIO.OUT)
def tongleLED(state, duration):
    GPIO.output(LED, state)
    time.sleep(duration)
try:
    while True:
        tongleLED(GPIO.HIGH, 1)
        tongleLED(GPIO.LOW, 2)
        tongleLED(GPIO.HIGH, 3)
        tongleLED(GPIO.LOW, 1)
except KeyboardInterrupt:
    GPIO.cleanup()
