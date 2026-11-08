# Cấu trúc tổng thể — Báo cáo Đồ án 2

Trạng thái: **chờ duyệt** (bản đề xuất, chưa viết nội dung).

## Thông tin chung
- Tên đề tài: Thiết kế hệ thống giám sát nhiệt độ, độ ẩm sử dụng AT89S52, ESP32-C3 và nền tảng IoT (lấy từ bản tóm tắt đề tài gốc).
- Sinh viên: Phạm Thanh Tuấn, Nguyễn Quốc Sinh. Lớp: Kỹ thuật điện tử - viễn thông K46. GVHD: TS Nguyễn Đỗ Dũng (theo bản tóm tắt gốc).
- Người đọc: giảng viên hướng dẫn, hội đồng chấm. Ngôn ngữ: tiếng Việt.
- Mẫu: bìa Trường Đại học Quy Nhơn (khung, logo Khoa Kỹ thuật và Công nghệ). Phần thân: A4, Times New Roman 13, mỗi chương sang trang mới, mục lục tự động — trừ khi khoa có quy định khác.
- Nguồn nội dung: repo này (firmware v0.2.0, sơ đồ KiCad, BOM, wiring.md, dashboard), bản tóm tắt đề tài, datasheet linh kiện (ghi trích dẫn).

## Mục lục dự kiến
| Phần | Nội dung chính | Độ dài tương đối | Đầu ra |
|---|---|---|---|
| Bìa, lời cảm ơn, mục lục, danh mục hình/bảng/viết tắt | | — | |
| Mở đầu | Lý do chọn đề tài, mục tiêu, phạm vi, phương pháp, bố cục báo cáo | ngắn | |
| Chương 1. Tổng quan và cơ sở lý thuyết | IoT giám sát môi trường; AT89S52; ESP32-C3; DHT11 (giao thức 1 dây); OLED SSD1315 (I²C); UART; TXS0108E chuyển mức; relay + opto PC817; LM7805; ThingsBoard, MQTT/HTTP, NTP | dài | Hình chân/khối linh kiện, bảng so sánh |
| Chương 2. Thiết kế phần cứng | Sơ đồ khối; khối nguồn (jack/domino 12 V → SR360 → LM7805); khối vi điều khiển, reset, thạch anh, ISP; cảm biến, nút; OLED; chuyển mức và ESP32; khối relay cách ly; sơ đồ nguyên lý KiCad; thiết kế PCB (100×100 mm, net class); BOM và chi phí | dài | Sơ đồ nguyên lý, ảnh PCB, bảng nối chân, BOM |
| Chương 3. Thiết kế phần mềm | Firmware AT89S52 (đọc DHT11, OLED 2 trang, khung truyền UART, relay trễ 32/30 °C); firmware ESP32-C3 (Wi-Fi, NTP, gửi telemetry, OE); giao thức khung truyền; dashboard ThingsBoard (12 widget, cảnh báo, CSV) | dài | Lưu đồ, bảng khung truyền, ảnh dashboard |
| Chương 4. Thi công, kiểm thử và đánh giá | Chế tạo mạch, nạp chương trình, kịch bản kiểm thử, kết quả đo, đánh giá | trung bình | **Phụ thuộc số liệu đo thật** — chưa có |
| Kết luận và hướng phát triển | Kết quả đạt được, hạn chế, hướng phát triển | ngắn | |
| Tài liệu tham khảo | Datasheet, tài liệu Espressif/ThingsBoard | | |
| Phụ lục | Sơ đồ nguyên lý đầy đủ, BOM, trích mã nguồn | | |

## Hình/bảng dự kiến
- Lấy từ repo: sơ đồ nguyên lý (xuất PDF/PNG từ KiCad), ảnh 3D/layout PCB, BOM, bảng nối chân từ `hardware/wiring.md`, ảnh dashboard (xuất từ bản local).
- Vẽ mới: sơ đồ khối, lưu đồ firmware AT89S52 và ESP32.
- Ảnh mạch thật, ảnh đo: chỉ dùng khi người dùng cung cấp.

## Bìa
Mẫu bìa Quy Nhơn; ảnh bìa: không dùng ảnh (chỉ khung + logo + chữ) — chờ xác nhận.
