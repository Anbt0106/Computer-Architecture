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


def handle_BT1(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT1) == GPIO.LOW:  # Nếu 1 được bấm
            print("BT1 is pressed")
            is_pressed_BT3.value = False  # Tắt trạng thái BT3
            pressed_time_BT4.value = 0  # Tắt trạng thái BT4
            GPIO.output(LED, GPIO.HIGH)  # Bật LED
            time.sleep(0.15)


def handle_BT2(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT2) == GPIO.LOW:  # Nếu Bt2 đc bấm
            print("BT2 is pressed")
            is_pressed_BT3.value = False
            pressed_time_BT4.value = 0
            GPIO.output(LCD, GPIO.HIGH)  # Bật LCD
            time.sleep(0.15)


def handle_BT3(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT3) == GPIO.LOW:  # Nếu BT3 đc bấm
            print("BT3 is pressed")
            is_pressed_BT3.value = True  # Bật trạng thái BT3
            pressed_time_BT4.value = 0
        if is_pressed_BT3.value:  # Nếu BT3 đc bấm
            GPIO.output(LED, GPIO.LOW)  # Tắt LED
        time.sleep(0.15)


def handle_BT4(is_pressed_BT3, pressed_time_BT4):
    while True:
        if GPIO.input(BT4) == GPIO.LOW:  # Nếu BT4 đc bấm
            print("BT4 is pressed")
            is_pressed_BT3.value = False
            pressed_time_BT4.value = (pressed_time_BT4.value % 2) + 1
            GPIO.output(LCD, GPIO.LOW)  # Tắt LCD
        time.sleep(0.15)


def main():
    pressed_time_BT4 = Value('d', 0)
    is_pressed_BT3 = Value('i', False)

    Process(target=handle_BT1, args=(is_pressed_BT3, pressed_time_BT4)).start()
    Process(target=handle_BT2, args=(is_pressed_BT3, pressed_time_BT4)).start()
    Process(target=handle_BT3, args=(is_pressed_BT3, pressed_time_BT4)).start()
    Process(target=handle_BT4, args=(is_pressed_BT3, pressed_time_BT4)).start()


try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
