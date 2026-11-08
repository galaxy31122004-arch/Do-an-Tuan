# Nội dung đã xác nhận và giới hạn cập nhật

## Đã xác nhận
- Cập nhật: dùng module TXS0108E cho I²C/UART, OE từ GPIO6; dùng Burn-E nạp/verify HEX AT89S52, bỏ bước cài/build compiler trên máy này.
- AT89S52 giữ vai trò xử lý đo và hiển thị; ESP32 phụ trách mạng, trao đổi với AT89S52 qua UART.
- Giữ DHT11; bỏ RTC, thạch anh 32,768 kHz và pin dự phòng. ESP32 lấy NTP và gửi giờ UTC cho AT89S52 hiển thị UTC+7.
- Đổi LCD 2004 sang OLED trắng 0,96 inch I²C dùng SSD1315 theo module người dùng chọn.
- Hai trang OLED, nút chuyển trang; hiển thị số đo, thời gian và trạng thái kết nối.
- Mạch thật kết nối Internet; một thiết bị và một tài khoản chủ thiết bị.
- Lưu thời gian đo, nhiệt độ, độ ẩm, mã thiết bị; dashboard số đo, lịch sử, lọc thời gian, xuất CSV; cấu hình ngưỡng và lịch sử cảnh báo.
- Mất mạng vẫn đo và hiển thị; tự kết nối lại; phiên bản đầu không lưu bù.
- Dùng nền tảng có sẵn như ThingsBoard; đây là yêu cầu thiết kế, không phải tuyên bố mọi bản dịch vụ đều sẵn tất cả tính năng.

## Phạm vi từng mục
- Mục 1: giải thích ngắn nhu cầu; không khẳng định kết quả hoặc độ chính xác chưa đo.
- Mục 2: liệt kê mục tiêu theo phạm vi đã duyệt.
- Mục 3: thể hiện đầy đủ nguồn, đo, xử lý, hiển thị và kết nối từ xa.
- Mục 4: mô tả luồng và xử lý lỗi; cảnh báo ngưỡng thực hiện trên nền tảng/web, chưa yêu cầu còi hoặc điều khiển tải.
- Mục 5: kế hoạch kiểm thử, không ghi thành kết quả đã đạt.

## Chưa chốt và không suy đoán
- Dịch vụ/bản triển khai cụ thể, gói tính năng và giao thức truyền cloud.
- Chu kỳ đo/gửi, ngưỡng cảnh báo, thời gian lưu dữ liệu.
- Bảng nối dây và chuyển mức TXS0108E đã có; footprint, pinout module/cáp Burn-E và driver OLED cần đối chiếu phần cứng thực tế.
- Không thêm thông số điện áp, địa chỉ bus hoặc thông số cảm biến chưa kiểm chứng vào bản tóm tắt.

## Bàn giao
Bản Word mới giữ cấu trúc năm mục, bản gốc giữ nguyên. Nội dung là mục tiêu thiết kế để người dùng và giảng viên xem xét, không phải báo cáo kết quả thực nghiệm.
