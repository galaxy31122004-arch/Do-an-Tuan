# Nguồn kỹ thuật

Ngày tra cứu: 2026-11-01. Các lựa chọn chức năng xuất phát từ phạm vi người dùng đã duyệt; thông số chân/điện và API phải đối chiếu tài liệu gốc khi chế tạo.

- **RSCH-20261101-0001:** [ThingsBoard HTTP device API](https://thingsboard.io/docs/reference/http-api/): HTTPS POST telemetry, token thiết bị, payload timestamped.
- **RSCH-20261101-0002:** [Microchip PIC16F87XA DS39582C (thiết kế cũ)](https://ww1.microchip.com/downloads/en/DeviceDoc/39582C.pdf): nguồn lịch sử của thiết kế PIC, không dùng cho AT89S52.
- **RSCH-20261101-0003:** [Dashboard Thermostats chính thức](https://github.com/thingsboard/thingsboard/blob/master/application/src/main/data/json/demo/dashboards/thermostats.json), [system widget defaults](https://github.com/thingsboard/thingsboard/tree/master/application/src/main/data/json/system/widget_types): schema dashboard, biểu đồ, bảng và form attributes. Generator dùng upstream master; file JSON đi kèm là snapshot của lần tạo.
- **RSCH-20261101-0004:** [Module OLED người dùng chọn](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c): seller ghi SSD1315 nhưng tài liệu tải về có tên SSD1306, cần kiểm tra module thực tế.

- **RSCH-20261101-0005:** [TI TXS0108E](https://www.ti.com/product/TXS0108E), [datasheet](https://www.ti.com/lit/ds/symlink/txs0108e.pdf): chuyển mức I²C/UART, pull-up nội, OE và hai nguồn VCCA/VCCB.
- **Thông tin người dùng:** dùng Burn-E để nạp AT89S52; đã đọc phần mềm Burn-E Programmer 9.00.88 và pinout AT89S52 tại máy. Chưa xác nhận chiều cáp/mạch đế thực tế hoặc Verify phần cứng.

Chưa có kết quả thực nghiệm phần cứng. Không có cam kết độ chính xác cảm biến hoặc hiệu năng mạng chưa đo.

- **RSCH-20261101-0006:** [ThingsBoard Docker](https://thingsboard.io/docs/user-guide/install/docker/): bản cài CE cục bộ, PostgreSQL và bước khởi tạo dữ liệu.
- **RSCH-20261101-0007:** [Device profile model](https://github.com/thingsboard/thingsboard/blob/master/ui-ngx/src/app/shared/models/device.models.ts), [query model](https://github.com/thingsboard/thingsboard/blob/master/ui-ngx/src/app/shared/models/query/query.models.ts): alarm rules với ngưỡng động từ attributes; cấu hình đã chạy trên bản local.
- **RSCH-20261101-0008:** [ESP32-C3 UART](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/uart.html): dùng UART1 và GPIO matrix; SuperMini chọn GPIO4/5, OE GPIO6.
- **RSCH-20261101-0009/0010:** giá bán IC/module và linh kiện nhỏ ngày 01/11/2026; xem liên kết từng dòng tại `hardware/cost-estimate.md`. PCB120.000đ do người dùng cung cấp, không phải giá tra từ nhà sản xuất.

- **RSCH-20261101-0011:** [Microchip AT89S52 doc1919](https://ww1.microchip.com/downloads/en/DeviceDoc/doc1919.pdf): pinout, reset mức cao, ISP, 8 KB Flash/256 byte RAM. [AT89S52-24PU 27.000đ](https://chotroihn.vn/at89s52-24pu-dip40), [nguồn khác 79.000đ](https://icdayroi.com/at89s52-24pu), [thạch anh 11,0592 MHz 1.500đ](https://icdayroi.com/thach-anh-11-0592mhz-hc49-dip).
- Kiểm tra tại máy: Burn-E Programmer 9.00.88 có AT89S52, hiển thị pinout RST9/VCC40/GND20/MISO7/SCK8/MOSI6, yêu cầu crystal18/19 và EA31 lên VCC. Đây chưa phải bằng chứng mạch nạp/chip kết nối hay Verify PASS.

- **RSCH-20261101-0012:** [SDCC Windows portable snapshot](https://sourceforge.net/projects/sdcc/files/snapshot_builds/x86_64-w64-mingw32/), bản 20261031/#17109 báo 4.6.4; [thư viện target mcs51 small từ bản chính thức 4.5.0](https://sourceforge.net/projects/sdcc/files/sdcc-linux-amd64/4.5.0/). Windows snapshot chỉ có compiler, nên dùng các thư viện target độc lập hệ điều hành này; hash từng thư viện và compiler ghi trong build-info.json. Đã link và thử runtime bằng uCsim; ghi rõ cấu hình này để tái lập, không mô tả là một bộ cài SDCC4.5 đồng nhất.
