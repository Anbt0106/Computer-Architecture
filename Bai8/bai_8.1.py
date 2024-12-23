import RPi.GPIO as GPIO
import time

SERVO = 6

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)


def set_servo_angle(angle):
    duty = angle / 18
    GPIO.output(SERVO, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(SERVO, False)
    pwm.ChangeDutyCycle(0)


def main():
    while True:
        set_servo_angle(20)
        set_servo_angle(160)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
