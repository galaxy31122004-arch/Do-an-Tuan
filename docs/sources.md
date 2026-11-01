# Nguồn kỹ thuật

Ngày tra cứu: 2026-11-01. Các lựa chọn chức năng xuất phát từ phạm vi người dùng đã duyệt; thông số chân/điện và API phải đối chiếu tài liệu gốc khi chế tạo.

- **RSCH-20261101-0001:** [ThingsBoard HTTP device API](https://thingsboard.io/docs/reference/http-api/): HTTPS POST telemetry, token thiết bị, payload timestamped.
- **RSCH-20261101-0002:** [Microchip PIC16F87XA DS39582C](https://ww1.microchip.com/downloads/en/DeviceDoc/39582C.pdf), [TI SN74AHCT125](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf): pinout và chuyển mức UART.
- **RSCH-20261101-0003:** [Dashboard Thermostats chính thức](https://github.com/thingsboard/thingsboard/blob/master/application/src/main/data/json/demo/dashboards/thermostats.json), [system widget defaults](https://github.com/thingsboard/thingsboard/tree/master/application/src/main/data/json/system/widget_types): schema dashboard, biểu đồ, bảng và form attributes. Generator dùng upstream master; file JSON đi kèm là snapshot của lần tạo.
- **RSCH-20261101-0004:** [Module OLED người dùng chọn](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c): seller ghi SSD1315 nhưng tài liệu tải về có tên SSD1306, cần kiểm tra module thực tế.

Chưa có kết quả thực nghiệm phần cứng. Không có cam kết độ chính xác cảm biến hoặc hiệu năng mạng chưa đo.
