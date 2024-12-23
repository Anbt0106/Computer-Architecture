
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 13
BT_1 = 21
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
ledState = False  # Trạng thái ban đầu của led


def updateLED():
    global ledState  # Sử dụng biến ledState ở ngoài hàm
    if GPIO.input(BT_1) == GPIO.LOW:  # Nút nhấn được nhấn
        ledState = not ledState  # Đảo trạng thái led
        GPIO.output(LED, ledState)  # Bật/tắt led
        time.sleep(0.25)


try:
    while True:
        updateLED()
except KeyboardInterrupt:
    GPIO.cleanup()
