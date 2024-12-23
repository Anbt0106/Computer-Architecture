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
TRIG = 15
ECHO = 4
DIR_PIN = 25
PWM_PIN = 24
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm_dc = GPIO.PWM(PWM_PIN, 100)
mode_dict = {0: "Live", 1: "Video"}


def motor_control(speed, dir):
    GPIO.output(DIR_PIN, dir)
    if dir == 0:
        speed = speed
    else:
        speed = 100 - speed
    pwm_dc.ChangeDutyCycle(speed)


motor_control(0, 0)


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


def show_screen(distance, mode):
    lcd_init()
    time.sleep(1)
    lcd_clear()
    GPIO.output(LCD_PINS['BL'], True)
    time.sleep(1)
    while 1:
        lcd_display_string('Distance:{} cm'.format(distance.value), 1)
        lcd_display_string('Mode:{}'.format(mode_dict[mode.value]), 2)
        time.sleep(0.5)


def read_bts(t_h_setting, *args):
    def pull_up_bts():
        for pin in BTS.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pull_up_bts()
    while 1:
        if GPIO.input(BTS['BT1']) == 0:
            t_h_setting[:] = [1, 0, 0, 0]
        if GPIO.input(BTS['BT2']) == 0:
            t_h_setting[1] = 1
        if GPIO.input(BTS['BT3']) == 0:
            t_h_setting[2] = 1
        else:
            t_h_setting[2] = 0
        if GPIO.input(BTS['BT4']) == 0:
            t_h_setting[0] = [0, 0, 0, 1]
        time.sleep(0.5)


def control_sensor(check_bts, distance, mode):
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    while 1:
        if not check_bts[1] and check_bts[0]:
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
            dist = round(dist, 1)
            if dist > 100:
                print("ERRORm, try again")
            else:
                distance.value = dist
                print("Distance: %s" % dist)
                if dist < 5:
                    mode.value = 1
                else:
                    mode.value = 0
            time.sleep(1)


def control_DC(check_bts, distance):
    pwm_dc.start(0)
    speed = 10
    is_bt3_press = False
    while 1:
        if check_bts[2]:
            is_bt3_press = True
            speed = speed + 10
            if speed > 100:
                speed = 100
        elif not check_bts[2] and (check_bts[0] or check_bts[1]) and is_bt3_press:
            speed = speed - 10
            if speed < 0:
                is_bt3_press = False
                check_bts[:] = [0, 0, 0, 0]
                speed = 10
        if check_bts[3]:
            motor_control(0, 0)
            check_bts[:] = [0, 0, 0, 0]
            speed = 10
        if not check_bts[1] and check_bts[0]:
            motor_control(speed, 0)
        elif check_bts[1]:
            motor_control(speed, 1)
        time.sleep(1)


def main(check_bts, distance, mode):
    Process(target=read_bts, args=(check_bts,)).start()
    Process(target=control_sensor, args=(check_bts, distance, mode)).start()
    Process(target=show_screen, args=(distance, mode)).start()
    Process(target=control_DC, args=(check_bts, distance)).start()
    global namewindow
    namewindow = "Camera User"
    capture = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc(*'MJPG'), 20.0, (640, 480))
    closed = True
    while 1:
        if check_bts[0]:
            ret, frame = capture.read()
            if mode.value == 1:
                out.write(frame)
            if not check_bts[1]:
                cv2.imshow(namewindow, frame)
                closed = False
            else:
                if not closed:
                    cv2.destroyWindow(namewindow)
                    closed = True
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyWindow(namewindow)
                out.release()
                break


if __name__ == "__main__":
    try:
        distance = Value('d', 100)
        check_bts = Array('i', [0 for _ in range(4)])
        mode = Value('i')
        main(check_bts, distance, mode)
    except KeyboardInterrupt:
        GPIO.cleanup()
