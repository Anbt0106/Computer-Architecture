import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PWM_PIN = 24
DIR_PIN = 25
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)


def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)


def main():
    while True:
        motor_control(50, 0)


try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
