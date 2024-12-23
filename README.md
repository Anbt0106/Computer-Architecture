# Computer-Architecture

## 1. Điều Khiển LED và LCD
- **Kịch bản:**
  - Nhấn lần lượt theo thứ tự nút bấm 1, nút bấm 2 thì LED sáng.
  - Nhấn lần lượt theo thứ tự nút bấm 3, nút bấm 4 thì đèn LCD sáng.
  - Nhấn giữ đồng thời nút bấm 1 và nút bấm 3 thì cả hai LED và đèn LCD tắt.

---

## 2. Hiển Thị Chữ Trên LCD 16x2
- **Kịch bản:**
  - Nhấn nút bấm 1 lần 1: từng ký tự trong chữ "Hello-World" chạy từ phải sang trái trên màn hình LCD 16x2.
  - Nhấn nút bấm 1 lần 2: từng ký tự trong chữ "Hello-World" chạy từ trái sang phải trên màn hình LCD 16x2.
  - Nhấn nút bấm 1 lần 3: xóa trắng màn hình.

---

## 3. Menu Tương Tác 4 Cấp Trên LCD
- **Chức năng:**
  - Nút bấm 1: có vai trò phím quay lại.
  - Nút bấm 2 và 3: di chuyển lên/xuống.
  - Nút bấm 4: chọn menu.
  - Cấp 1: menu chính.
  - Cấp 2: menu 1, menu 2.
  - Cấp 3: menu 1_1, menu 2_2.
  - Cấp 4: bật/tắt LED, role-1, role-2.

---

## 4. Nhập Mật Khẩu và Hiển Thị Bảo Mật Trên LCD
- **Kịch bản:**
  - Nhấn nút bấm 1 để chọn số (0-9) trong 0.5s, số cuối cùng được chọn sẽ hiển thị.
  - Sau khi nhập số, các ký tự sẽ chuyển sang dạng `****` để bảo mật.
  - Nếu mật khẩu là "999", bật role-1 và hiển thị "Thành công" trên LCD.

---

## 5. Điều Khiển Bộ Nhiệt Độ
- **Chức năng:**
  - Khi nhiệt độ tăng cao hơn nhiệt độ phòng: bật role-1 và role-2.
  - Khi nhiệt độ bằng nhiệt độ phòng: tắt role-2.
  - Khi nhiệt độ nhỏ hơn nhiệt độ phòng: tắt cả hai role.
  - Hiển thị nhiệt độ trên LCD.

---

## 6. Điều Khiển Nhiệt Độ và Độ Ẩm
- **Kịch bản:**
  - Hệ thống đếm số người trong phòng.
  - Khi số người > 0,  đo nhiệt độ và độ ẩm trong phòng, nếu:
    - Nhỏ hơn ngưỡng: bật role-1.
    - Lớn hơn ngưỡng: bật role-2.
  - Hiển thị nhiệt độ, độ ẩm và số người trên LCD.

---

## 7. Điều Khiển Động Cơ Một Chiều
  - Nhấn nút bấm 1:
    - Lần 1: động cơ quay theo chiều bất kỳ với tốc độ 20%.
    - Lần 2: tăng tốc lên 40%.
    - Lần 3: tăng tốc lên 100%.
    - Lần 4: dừng quay ngay lập tức.
  - Nhấn nút bấm 2: động cơ đảo chiều với cùng kịch bản.

## 8. Điều Khiển Động Cơ Một Chiều
  - Nhấn nút bấm 1 và giữ: Động cơ quay theo chiều bất kì, tăng tốc 10% mỗi giây đến 100%, sau đó giữ tốc độ.
  - Nếu nhả nút bấm 1: động cơ quay theo quán tính và dừng hẳn khi hết quán tính.
  - Nhấn nút bấm 3 và giữ: động cơ đảo chiều quay với cùng kịch bản khi nhấn nút bấm 1.
  - Trong quá trình đang quay, nếu nhấn nút bấm 2: động cơ dừng ngay lập tức.
  - Hiển thị trạng thái: chiều quay, tốc độ trên LCD.

---

## 9. Điều Khiển Động Cơ Một Chiều
  - Nhấn nút bấm 1 và giữ: Động cơ quay theo chiều bất kì, tăng tốc 10% mỗi giây đến 100%, sau đó giữ tốc độ.
  - Trong quá trình đang quay, nếu nhấn nút bấm 2: động cơ dừng ngay lập tức.
  - Hiển thị trạng thái: chiều quay, tốc độ trên LCD.

---
## 10. Điều Khiển RC-Servo
  - Nhấn nút bấm 1: RC-servo quay góc 20°.
  - Nhấn nút bấm 2: mở góc 60°.
  - Nhấn nút bấm 3: đóng góc 160°.
  - Hiển thị góc quay trên LCD.

---
## 11. Điều Khiển RC-Servo
  - Với mỗi lần nhấn nút bấm 1: RC-servo quay thêm 10°, khi quay đến góc 160° động cơ sẽ quay về góc 10°, lặp đi lặp lại quá trình này.
  - Hiển thị góc quay hiện tại trên LCD.

---

## 12. Hệ Thống Bơm Nước Tự Động
  - Sử dụng cảm biến siêu âm để đo khoảng cách đến mặt nước.
  - Nếu ....
  - Hiển thị khoảng cách trên LCD.

---

## 13. Mô phỏng hệ thống chống xâm nhập
  - Sử dụng cảm biến siêu âm để đo khoảng cách và phát hiện vật cản.
  - Khi phát hiện vật cản, bật LED cảnh báo.
  - Nếu khoảng cách nhỏ hơn ngưỡng, bật role-1. Nếu tiếp tục nhỏ hơn, kích hoạt động cơ một chiều.
  - Hiển thị mức cảnh báo và khoảng cách trên LCD.

---

## 14. Hình trái tim
  - Hiển thị hình trái tim trên LED ma trận 8x8.
  - Nhấn nút bấm 1: trái tim hiển thị/tắt liên tục theo chu kỳ 1s.

---

## 15. Xử Lý Hình Ảnh
  - Nhấn nút bấm 1: chụp ảnh từ cảm biến hình ảnh.
  - Nhấn nút bấm 2: tính tổng số pixel màu đỏ trong ảnh.
  - Hiển thị kết quả trên LCD.

## 16. Xử Lý Hình Ảnh
  - Nhấn nút bấm 1: chụp ảnh từ cảm biến hình ảnh.
  - Nhấn nút bấm 2: tính tổng số pixel màu xanh lá và màu đỏ trong ảnh.
  - So sánh 2 giá trị pixel màu xanh lá và màu đỏ, nếu:
    - Nếu màu đỏ > màu xanh lá: bật role-1.
    - Ngược lại: bật role-2.
