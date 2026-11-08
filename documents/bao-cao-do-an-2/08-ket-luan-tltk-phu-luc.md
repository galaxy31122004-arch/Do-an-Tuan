# KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## Kết luận

Đề tài đã hoàn thành thiết kế hệ thống giám sát nhiệt độ, độ ẩm sử dụng AT89S52, ESP32-C3 và nền tảng IoT ThingsBoard. Các kết quả gồm:

- **Phần cứng:**
  - khối nguồn 12 V/5 V có chống ngược cực;
  - khối vi điều khiển AT89S52;
  - cảm biến DHT11, màn hình OLED;
  - bộ chuyển mức TXS0108E nối với ESP32-C3;
  - khối relay điều khiển qua opto PC817.

  Sơ đồ nguyên lý đã vẽ trên KiCad, kiểm tra luật điện (ERC) đạt 0 lỗi. Mạch in hai lớp 92,5 × 84,7 mm đã đi dây hoàn chỉnh, kiểm tra luật thiết kế (DRC) không còn lỗi điện.
- **Firmware AT89S52:** đọc DHT11, hiển thị hai trang trên OLED, điều khiển relay có trễ (bật ở 32 °C, tắt ở 30 °C) và truyền khung dữ liệu có CRC.
- **Firmware ESP32-C3:** kết nối Wi-Fi, đồng bộ NTP, gửi dữ liệu lên ThingsBoard qua HTTPS và tự kết nối lại khi mất mạng.
- **Dashboard ThingsBoard:** hiển thị số đo, biểu đồ lịch sử, xuất CSV, ngưỡng và lịch sử cảnh báo, trạng thái relay.
- **Kiểm thử phần mềm:** các kiểm thử tự động đã đạt. Kế hoạch kiểm thử trên mạch thật đã được xây dựng.

Phần chế tạo và đo kiểm trên mạch thật chưa thực hiện. Kết quả sẽ được bổ sung để đánh giá đầy đủ hệ thống.

## Hướng phát triển

- Thay DHT11 bằng cảm biến chính xác hơn như SHT31 hoặc BME280.
- Lưu tạm dữ liệu khi mất mạng và gửi bù khi có kết nối trở lại.
- Cho phép chỉnh ngưỡng relay từ dashboard và gửi xuống thiết bị.
- Thay LM7805 bằng bộ nguồn xung để giảm tỏa nhiệt.
- Mở rộng thành nhiều thiết bị, nhiều người dùng; gửi thông báo cảnh báo qua email hoặc ứng dụng nhắn tin.

# TÀI LIỆU THAM KHẢO

[1] Atmel Corporation, *AT89S52: 8-bit Microcontroller with 8K Bytes In-System Programmable Flash*, Datasheet doc1919. [Trực tuyến]: https://ww1.microchip.com/downloads/en/DeviceDoc/doc1919.pdf

[2] Espressif Systems, *ESP32-C3 Series Datasheet* và *ESP-IDF Programming Guide – UART (ESP32-C3)*. [Trực tuyến]: https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/uart.html

[3] Aosong Electronics, *DHT11 Humidity & Temperature Sensor*, Datasheet.

[4] Solomon Systech, *SSD1315 128 × 64 Dot Matrix OLED Segment/Common Driver with Controller*, Datasheet.

[5] Texas Instruments, *TXS0108E 8-Bit Bidirectional Voltage-Level Translator for Open-Drain and Push-Pull Applications*, Datasheet. [Trực tuyến]: https://www.ti.com/lit/ds/symlink/txs0108e.pdf

[6] Sharp Corporation, *PC817 Series Photocoupler*, Datasheet.

[7] Texas Instruments, *LM78xx Fixed Voltage Regulators*, Datasheet.

[8] ThingsBoard, *ThingsBoard Community Edition Documentation*. [Trực tuyến]: https://thingsboard.io/docs/

[9] ThingsBoard, *HTTP Device API Reference*. [Trực tuyến]: https://thingsboard.io/docs/reference/http-api/

[10] SDCC, *Small Device C Compiler User Guide*. [Trực tuyến]: https://sdcc.sourceforge.net/

[11] KiCad, *KiCad 10 Documentation*. [Trực tuyến]: https://docs.kicad.org/

# PHỤ LỤC

## Phụ lục A. Bảng vật tư

(Bảng vật tư đầy đủ gồm 42 chi tiết, lấy từ `hardware/BOM.md`.)

## Phụ lục B. Sơ đồ nguyên lý

(Sơ đồ nguyên lý xuất từ KiCad.)

## Phụ lục C. Mã nguồn

Mã nguồn đầy đủ của firmware AT89S52 (`firmware/v0.2.0/at89s52/main.c`), firmware ESP32-C3 (`firmware/v0.2.0/esp32/src/main.cpp`) và giao thức dùng chung (`firmware/v0.2.0/common/protocol.h`) được lưu trong kho mã nguồn của đề tài.
