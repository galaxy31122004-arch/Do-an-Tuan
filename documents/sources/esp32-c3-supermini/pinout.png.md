# ESP32-C3 SuperMini — sơ đồ chân

- Nguồn: ảnh người dùng gửi trong phiên làm việc ngày 08/11/2026; không rõ shop/nguồn gốc ảnh.
- File: [pinout.png](pinout.png)
- Mục đích: đối chiếu thứ tự chân header ESP32 trên sơ đồ KiCad `hardware/pcb/env-monitor.kicad_sch`.

## Đọc được từ ảnh (nhìn mặt linh kiện, cổng USB-C hướng lên)

| Hàng | Từ trên xuống |
|---|---|
| Phải (J2A) | 5V, GND, 3V3, GPIO4, GPIO3, GPIO2, GPIO1, GPIO0 |
| Trái (J2B) | GPIO5, GPIO6, GPIO7, GPIO8, GPIO9, GPIO10, GPIO20 (RX), GPIO21 (TX) |

Ảnh còn ghi nhãn phụ: GPIO6/7 = SDA/SCL, GPIO8/9/10 = SCK/MISO/MOSI, GPIO20/21 = RX/TX (UART0). Firmware không dùng các nhãn này: UART1 RX=GPIO3, TX=GPIO4, OE TXS=GPIO0.

## Chưa xác định từ ảnh

- Ảnh không có thước. Khoảng cách hai hàng lấy theo thông số Protosupplies: 15,24 mm (0,6″), bo 22,5 × 18 mm, bước 2,54 mm (RSCH-20261109-0001, `docs/sources.md`). Footprint `ESP32-C3_SuperMini` dùng ±7,62 mm, khớp.
