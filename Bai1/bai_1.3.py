import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # số thứ tự của chân GPIO theo BCM
GPIO.setwarnings(False)  # tắt cảnh báo

led = 13
GPIO.setup(led, GPIO.OUT)  # chân GPIO là chân ra
count = 0  # biến đếm số lần nhấp nháy
try:
    while True:
        GPIO.output(led, GPIO.HIGH)  # bật đèn
        count += 1
        print('Đèn sáng {} lần'.format(count))
        time.sleep(1)  # đợi 1 giây
        GPIO.output(led, GPIO.LOW)  # tắt đèn
        time.sleep(1)  # đợi 1 giây
except KeyboardInterrupt:
    GPIO.cleanup()  # giải phóng tài nguyên
