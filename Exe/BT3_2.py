from multiprocessing import Process, Value
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BT1 = 21
BT2 = 26
BT3 = 20
BT4 = 19

LED = 13
LCD = 2

GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(LED, GPIO.OUT)
GPIO.setup(LCD, GPIO.OUT)

#Nhấn lần lượt BT1 rồi BT2 thì LED sáng, BT3 rồi BT4 thì LCD sáng
#Nhấn giữ đồng thời BT1 và BT3 thì LED, LCD tắt

def press_B

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()