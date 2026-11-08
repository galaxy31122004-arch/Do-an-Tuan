# Dàn ý slide — Đồ án 2 (bảo vệ/báo cáo)

Nguồn: `documents/bao-cao-do-an-2/` (Mở đầu → Chương 4), firmware v0.2.0, KiCad, BOM. Mẫu "Kem – xanh ngọc". 10 slide, mỗi slide nhiều nội dung. Chưa có số đo mạch thật → không có slide kết quả đo.

1. **Bìa (nền tối)** — BÁO CÁO ĐỒ ÁN 2; tên đề tài; Phạm Thanh Tuấn, Nguyễn Quốc Sinh; lớp ĐTVT K46; GVHD TS Nguyễn Đỗ Dũng; Trường ĐH Quy Nhơn – Khoa KT&CN.
2. **Đặt vấn đề & mục tiêu** — trái: hạn chế của nhiệt ẩm kế tại chỗ (không xem từ xa, không lịch sử, không cảnh báo); phải: 6 thẻ mục tiêu (đo DHT11/OLED, UART + TXS0108E, ESP32 Wi-Fi/NTP/ThingsBoard, dashboard + CSV + cảnh báo, relay trễ 32/30 °C, KiCad + BOM). Dòng phạm vi: 1 thiết bị, mất mạng vẫn đo/hiển thị/điều khiển.
3. **Sơ đồ khối (nền tối)** — hình sơ đồ khối; 3 thẻ vai trò: AT89S52 (đo–hiển thị–relay), ESP32-C3 (mạng), ThingsBoard (lưu trữ–dashboard–cảnh báo).
4. **Khối nguồn** — luồng J1/J7 → SR360 → +12V → LM7805 → +5V → ESP32 3V3; relay lấy +12V; thẻ số: tải ~180 mA, LM7805 ~1,2 W (ước tính), tản nhiệt qua đồng GND; bảng net class 0,5/1/2 mm.
5. **AT89S52 & ngoại vi** — Bảng phân bổ chân (P0.3/P0.4 I²C + R8/R9 kéo lên, P3.0/P3.1 UART, P3.2 DHT11, P3.3 nút, P2.0 relay, XTAL 11,0592 MHz, RST, ISP J3); thẻ: reset R1·C2 ≈ 100 ms, EA lên 5V, nạp Burn-E.
6. **Chuyển mức TXS0108E & ESP32-C3** — Bảng phân kênh A1/B1, A2/B2 (UART, ESP32 RX=GPIO3, TX=GPIO4), A7/B7, A8/B8 (I²C), OE=GPIO0 + R4 100k; thẻ: chọn kênh theo vị trí PCB (thẳng hàng, không chéo dây), trình tự bật OE sau 100 ms.
7. **Relay cách ly quang** — bảng linh kiện (R6, PC817, R5/R7, C1815, K1, D3, J6 COM/NO); thẻ số: LED ~1,7 mA, cuộn ~30 mA, base 1–2 mA; logic P2.0 thấp = bật, mặc định tắt khi reset/lỗi cảm biến; tải có điện khi ≥ 32 °C.
8. **Sơ đồ nguyên lý & PCB** — ảnh schematic + ảnh 3D PCB 92,5×84,7 mm; thẻ: ERC 0 lỗi, DRC 0 lỗi điện (GND phủ hai mặt), PCB 2 lớp đã đi dây; chi phí linh kiện 217.310đ + PCB 120.000đ (chưa gồm mục chưa có giá).
9. **Phần mềm** — bảng khung truyền M/S/T (chiều, nội dung, chu kỳ) + CRC-8; hai cột: AT89S52 (vòng 2 s, DHT11 hợp ngữ, relay trễ, OLED 2 trang) và ESP32 (task UART, HTTPS mỗi 10 s, không gửi số giả); dashboard 12 widget.
10. **Kế hoạch kiểm thử, kết luận & cảm ơn (nền tối)** — tóm tắt 16 kịch bản (nguồn, OLED, DHT11, UART, NTP, cloud, mất mạng, relay, cảnh báo, CSV); kết quả đã đạt: ERC 0 lỗi, kiểm thử phần mềm PASS; hạn chế & hướng phát triển; "Cảm ơn thầy và các bạn đã lắng nghe".

Ghi chú lời nói cho từng slide đặt trong `<aside>`.
