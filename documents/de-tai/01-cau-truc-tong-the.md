# Cấu trúc cập nhật bản tóm tắt đồ án

- Mục tiêu: cập nhật đề tài từ đo và hiển thị tại chỗ thành giám sát tại chỗ và qua Internet.
- Nguồn: bản Word gốc và các quyết định đã được người dùng đồng ý trong hội thoại.
- Độc giả: giảng viên hướng dẫn; ngôn ngữ: tiếng Việt; mức viết: tóm tắt theo tài liệu gốc.
- Giữ thông tin sinh viên, lớp, giảng viên và cấu trúc năm mục của bản gốc. Không thêm bìa hoặc ảnh bìa.
- Tên đề tài: thiết kế hệ thống giám sát nhiệt độ, độ ẩm sử dụng AT89S52, ESP32 và nền tảng IoT.

## Các mục
1. Lý do chọn đề tài: nhu cầu đo tại chỗ, lưu lịch sử và giám sát từ xa.
2. Mục tiêu: DHT11, NTP từ ESP32, AT89S52, OLED SSD1315, ESP32, dashboard và cảnh báo.
3. Sơ đồ khối: cảm biến → AT89S52 → OLED; AT89S52 ↔ ESP32 → Wi-Fi/Internet → nền tảng IoT → dashboard.
4. Nguyên lý hoạt động: thu thập, hiển thị, truyền bản ghi, lưu trữ, cảnh báo và xử lý lỗi.
5. Mô phỏng và kiểm tra: mô phỏng phần phù hợp và kiểm thử tích hợp bằng mạch thật.

## Trạng thái
Đã cập nhật thêm module TXS0108E cho I²C/UART và nạp/verify AT89S52 bằng Burn-E; bỏ module thời gian thực, dùng NTP từ ESP32. Bỏ bước cài/build compiler AT89S52 trên máy này theo yêu cầu; chưa có HEX AT89S52 được kiểm chứng.
Người dùng đã đồng ý kiến trúc, phạm vi cloud/web, đổi OLED và yêu cầu cập nhật tài liệu. Bổ sung mới nhất: dùng nền tảng có sẵn như ThingsBoard. Không đặt thêm cổng duyệt cho các quyết định đã được chấp thuận.
