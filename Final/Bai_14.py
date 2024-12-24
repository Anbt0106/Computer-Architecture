import RPi.GPIO as GPIO
import time

# Viết chương trình hiển thị hình trái tim trên LED ma trận 8x8. Khi nhấn nút bấm 1, trái tim sẽ hiển thị và tắt liên tục theo chu kỳ 1s.
# Pin định nghĩa
CLK = 11
DIN = 10
CS = 8
BUTTON = 21  # Pin kết nối nút bấm (GPIO 21)

# Bảng ký tự (hình trái tim)
character = {
    'heart': [
        0x00,  # ........ (hàng 8)
        0x18,  # ...XX... (hàng 7)
        0x3C,  # ..XXXX.. (hàng 6)
        0x7E,  # .XXXXXX. (hàng 5)
        0xFF,  # XXXXXXXX (hàng 4)
        0xFF,  # XXXXXXXX (hàng 3)
        0x66,  # .XX..XX. (hàng 2)
        0x00  # ........ (hàng 1)
    ]
}

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(DIN, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Kéo lên nút bấm


# Hàm gửi dữ liệu qua giao thức SPI
def spi_send_byte(register, data):
    GPIO.output(CS, GPIO.LOW)
    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (register >> (7 - bit)) & 0x01)
        GPIO.output(CLK, GPIO.HIGH)
    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (data >> (7 - bit)) & 0x01)
        GPIO.output(CLK, GPIO.HIGH)
    GPIO.output(CS, GPIO.HIGH)


# Hàm khởi tạo MAX7219
def max7219_init():
    spi_send_byte(0x0F, 0x00)  # Tắt chế độ test
    spi_send_byte(0x09, 0x00)  # Không sử dụng decode
    spi_send_byte(0x0B, 0x07)  # Hiển thị 8 hàng
    spi_send_byte(0x0A, 0x0F)  # Độ sáng tối đa
    spi_send_byte(0x0C, 0x01)  # Bật thiết bị


# Hàm xóa màn hình LED
def clear_display():
    for row in range(1, 9):
        spi_send_byte(row, 0x00)


# Hàm hiển thị một mẫu (pattern) từ hàng 1 đến hàng 8
def display_pattern(pattern):
    for row in range(8):  # Hiển thị từ hàng 1 -> hàng 8
        spi_send_byte(row + 1, pattern[row])


# Chương trình chính
def main():
    max7219_init()
    clear_display()

    heart_display = False  # Trạng thái hiển thị trái tim

    while True:
        button_state = GPIO.input(BUTTON)

        if button_state == GPIO.LOW:  # Nút bấm được nhấn
            heart_display = not heart_display  # Đổi trạng thái hiển thị
            time.sleep(0.2)  # Tránh nhiễu nút bấm

        if heart_display:
            display_pattern(character['heart'])
            time.sleep(1)
            clear_display()
            time.sleep(1)
        else:
            clear_display()  # Không hiển thị gì nếu trạng thái tắt


try:
    main()
except KeyboardInterrupt:
    clear_display()
    GPIO.cleanup()
