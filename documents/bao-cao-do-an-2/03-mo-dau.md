# MỞ ĐẦU

## 1. Lý do chọn đề tài

Nhiệt độ và độ ẩm tương đối là hai thông số cần theo dõi thường xuyên trong sinh hoạt, bảo quản nông sản, thực phẩm, thiết bị điện tử và trong các mô hình giám sát môi trường. Các nhiệt ẩm kế hiển thị tại chỗ giúp người sử dụng quan sát giá trị tức thời, nhưng không cho phép theo dõi khi vắng mặt, không lưu lại diễn biến theo thời gian và không tự cảnh báo khi giá trị vượt ngưỡng.

Sự phát triển của Internet vạn vật (IoT) cùng các module Wi-Fi giá thấp như ESP32-C3 và các nền tảng IoT có sẵn như ThingsBoard cho phép bổ sung khả năng giám sát từ xa cho một hệ đo truyền thống mà không cần tự xây dựng máy chủ. Bên cạnh đó, vi điều khiển AT89S52 thuộc họ 8051 là đối tượng học tập quen thuộc trong chương trình đào tạo, phù hợp để thực hành lập trình nhúng ở mức thanh ghi: đọc cảm biến, giao tiếp I²C, UART và điều khiển ngoại vi.

Xuất phát từ nhu cầu trên, nhóm chọn đề tài **“Thiết kế hệ thống giám sát nhiệt độ, độ ẩm sử dụng AT89S52, ESP32-C3 và nền tảng IoT”**. Hệ thống vừa đo và hiển thị tại chỗ, vừa truyền dữ liệu qua Internet để lưu trữ, xem biểu đồ và cảnh báo trên trình duyệt, đồng thời có ngõ ra relay để đóng cắt tải (ví dụ quạt) theo nhiệt độ.

## 2. Mục tiêu của đề tài

- Lập trình AT89S52 đọc nhiệt độ, độ ẩm từ cảm biến DHT11 và hiển thị trên màn hình OLED 0,96 inch (SSD1315, giao tiếp I²C) với hai trang thông tin, chuyển trang bằng nút nhấn.
- Thiết kế giao tiếp UART giữa AT89S52 và ESP32-C3, có module TXS0108E chuyển mức logic giữa phía 5 V và phía 3,3 V.
- Lập trình ESP32-C3 kết nối Wi-Fi, đồng bộ giờ NTP, gửi dữ liệu lên nền tảng ThingsBoard và tự kết nối lại khi mất mạng.
- Xây dựng dashboard web hiển thị số đo mới nhất, biểu đồ lịch sử, lọc theo thời gian, xuất CSV và cảnh báo vượt ngưỡng.
- Điều khiển relay qua opto cách ly PC817 theo nhiệt độ có trễ (bật khi ≥ 32,0 °C, tắt khi ≤ 30,0 °C).
- Thiết kế sơ đồ nguyên lý và mạch in trên KiCad; lập bảng vật tư và dự toán chi phí.
- Xây dựng kế hoạch kiểm thử cho toàn bộ luồng đo, hiển thị, truyền dữ liệu và điều khiển.

## 3. Đối tượng và phạm vi nghiên cứu

- **Đối tượng:** vi điều khiển AT89S52, module ESP32-C3 SuperMini, cảm biến DHT11, màn hình OLED SSD1315, module chuyển mức TXS0108E, mạch relay cách ly quang và nền tảng ThingsBoard.
- **Phạm vi:**
  + Một thiết bị đo và một tài khoản chủ thiết bị trên nền tảng IoT.
  + Cảnh báo ngưỡng thực hiện trên nền tảng/web; relay điều khiển tại chỗ theo ngưỡng cố định trong firmware.
  + Khi mất mạng, hệ thống vẫn đo, hiển thị và điều khiển relay; phiên bản này không lưu bù dữ liệu trong thời gian mất kết nối.
  + Báo cáo trình bày thiết kế và kế hoạch kiểm thử; kết quả đo trên mạch thật sẽ được bổ sung sau khi chế tạo.

## 4. Phương pháp nghiên cứu

- Nghiên cứu tài liệu: datasheet linh kiện, tài liệu kỹ thuật của Espressif và ThingsBoard.
- Thiết kế phần cứng trên KiCad 10: sơ đồ nguyên lý, kiểm tra luật điện (ERC), bố trí mạch in.
- Lập trình nhúng: AT89S52 bằng ngôn ngữ C với trình biên dịch SDCC; ESP32-C3 bằng Arduino framework trên PlatformIO.
- Kiểm thử phần mềm tự động (kiểm tra giao thức, tệp HEX, cấu hình dashboard) và kiểm thử tích hợp trên mạch thật.

## 5. Bố cục báo cáo

Ngoài phần Mở đầu, Kết luận, Tài liệu tham khảo và Phụ lục, báo cáo gồm bốn chương:

- **Chương 1. Tổng quan và cơ sở lý thuyết:** giới thiệu hệ thống IoT giám sát môi trường và các linh kiện, giao thức sử dụng.
- **Chương 2. Thiết kế phần cứng:** sơ đồ khối, thiết kế từng khối, sơ đồ nguyên lý, mạch in và bảng vật tư.
- **Chương 3. Thiết kế phần mềm:** firmware AT89S52, firmware ESP32-C3, giao thức truyền và dashboard.
- **Chương 4. Thi công, kiểm thử và đánh giá:** quy trình chế tạo, nạp chương trình và kế hoạch kiểm thử.
