import RPi.GPIO as GPIO
import time

BT_1 = 21
BT_2 = 26
RELAY_1 = 16
RELAY_2 = 12
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)

def print_relay_status():
    print("RELAY 1 is " + ("ON" if GPIO.input(RELAY_1) else "OFF"))
    print("RELAY 2 is " + ("ON" if GPIO.input(RELAY_2) else "OFF"))

def main():
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            GPIO.output(RELAY_1, GPIO.HIGH)
            GPIO.output(RELAY_2, GPIO.LOW)
            print("Button 1 is pressed")
            print_relay_status()
            time.sleep(0.25)
        if GPIO.input(BT_2) == GPIO.LOW:
            GPIO.output(RELAY_1, GPIO.LOW)
            GPIO.output(RELAY_2, GPIO.HIGH)
            print("Button 2 is pressed")
            print_relay_status()
            time.sleep(0.25)

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()