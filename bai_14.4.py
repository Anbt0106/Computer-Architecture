import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Array, Value
import cv2

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS = {"BT1": 21, "BT2": 26, "BT3": 20, "BT4": 19}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
RELAY_1 = 15
TRIG = 15
ECHO = 4
LED = 13
DIR_PIN = 25
PWM_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm_dc = GPIO.PWM(PWM_PIN, 100)


def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)


def lcd_clear():
    lcd_byte(0x01, LCD_CMD)


def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)


def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


def motor_control(speed, dir):
    GPIO.output(DIR_PIN, dir)
    if dir == 0:
        speed = speed
    else:
        speed = 100 - speed
    pwm_dc.ChangeDutyCycle(speed)


motor_control(0, 0)


def show_screen(level, *args):
    lcd_init()
    time.sleep(2)
    lcd_clear()
    GPIO.output(LCD_PINS['BL'], True)
    time.sleep(1)
    while 1:
        lcd_display_string("Alert Level", 1)
        lcd_display_string(str(level.value), 2)
        time.sleep(0.5)


def control_sensor(level, *args):
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    while 1:
        time.sleep(1)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        dist = pulse_duration * 17150
        dist = round(dist, 2)
        if dist > 100:
            print("ERROR, try again")
        else:
            print("Distance: %s" % dist)
            if dist > 35:
                level.value = 0
            elif dist > 30:
                level.value = 1
            elif dist > 20:
                level.value = 2
            elif dist > 10:
                level.value = 3
            elif dist > 5:
                level.value = 4
        time.sleep(1)


def control_led_relay_dc(level, *args):
    GPIO.setup(RELAY_1, GPIO.OUT)
    GPIO.output(RELAY_1, GPIO.LOW)
    GPIO.setup(LED, GPIO.OUT)
    speed = 50
    pwm_dc.start(0)
    while 1:
        if level.value >= 1:
            if GPIO.input(LED) == GPIO.LOW:
                GPIO.output(LED, GPIO.HIGH)
            elif GPIO.input(LED) == GPIO.HIGH:
                GPIO.output(LED, GPIO.LOW)
        else:
            GPIO.output(LED, GPIO.LOW)
        if level.value >= 2:
            GPIO.output(RELAY_1, GPIO.HIGH)
        else:
            GPIO.output(RELAY_1, GPIO.LOW)
        if level.value == 4:
            motor_control(speed, 0)
        else:
            motor_control(0, 0)
        time.sleep(1)


def main(level):
    Process(target=control_sensor, args=(level,)).start()
    Process(target=control_led_relay_dc, args=(level,)).start()
    Process(target=show_screen, args=(level,)).start()
    namewindow = "Camera User"
    capture = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    time1 = None
    closed = None
    ids = 1
    out = None
    while 1:
        if level.value >= 2:
            ret, frame = capture.read()
            if level.value == 4:
                if not time1:
                    out = cv2.VideoWriter(f'output{ids}.avi', cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640, 480))
                    time1 = time.time()
                else:
                    if time.time() - time1 < 30:
                        out.write(frame)
                    else:
                        time1 = None
                        out.release()
                        out = None
                        ids += 1
            else:
                if time1:
                    time1 = None
                if out:
                    out.release()
                    out = None
                    ids += 1
            closed = False
            cv2.imshow(namewindow, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyWindow(namewindow)
                out.release()
                break
        else:
            if not closed:
                cv2.destroyWindow(namewindow)
                closed = True
            time.sleep(1)


if __name__ == "__main__":
    try:
        level = Value('i')
        main(level)
    except KeyboardInterrupt:
        GPIO.cleanup()
