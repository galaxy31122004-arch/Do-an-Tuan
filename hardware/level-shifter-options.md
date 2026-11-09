# Phương án đã chọn: module TXS0108E

Người dùng đã chọn một module TXS0108E để chuyển mức giữa AT89S52 5 V và OLED/ESP32 3,3 V. BOM, bảng chân, SVG và firmware ESP32 dùng chung phương án này.

TI công bố hỗ trợ open-drain và push-pull, VCCA 1,4–3,6 V, VCCB 1,65–5,5 V và VCCA ≤ VCCB. Với mạch này: A=3,3 V, B=5 V. Module cần dây ngắn, nguồn lọc tốt và OE điều khiển đúng mức VCCA.

## Ánh xạ kênh (theo PCB bản cuối)

| Kênh TXS0108E | Phía A (3,3 V) | Phía B (5 V) |
|---|---|---|
| A1/B1 | ESP32 GPIO3 (RX) | AT89S52 P3.1 TX chân 11 |
| A2/B2 | ESP32 GPIO4 (TX) | AT89S52 P3.0 RX chân 10 |
| A7/B7 | OLED SCL | AT89S52 P0.4 chân 35 (R9 10 kΩ kéo lên 5 V) |
| A8/B8 | OLED SDA | AT89S52 P0.3 chân 36 (R8 10 kΩ kéo lên 5 V) |
| A3–A6/B3–B6 | NC | NC |

GND chung; VCCA=3,3 V; VCCB=5 V. OE nối ESP32 GPIO0 và R4 100 kΩ xuống GND. Firmware giữ OE thấp, chờ 100 ms cho nguồn ổn định rồi bật; kiểm tra module không kéo cứng OE lên nguồn. Tụ lọc VCCA/VCCB có sẵn trên module. Không cấp 5 V vào OE/GPIO0; không thêm chia áp vào đường đã qua TXS.

Đã bỏ cặp MOSFET, buffer và chia áp cũ; U4 nay là module TXS0108E. Phía A dùng pull-up nội của TXS và pull-up có sẵn trên OLED. Phía B bắt buộc có R8/R9 vì P0 của AT89S52 là cực máng hở, không có pull-up nội. Đo dạng sóng I²C khi thử. J5A/J5B dự kiến hai header 1x10, phải đo module thực tế. Các kênh còn lại để NC.

Nguồn chính thức: [TI TXS0108E](https://www.ti.com/product/TXS0108E), datasheet trên cùng trang. Thông số hãng đã đọc ngày 2026-11-01 (RSCH-20261101-0005). Việc chuyển module cụ thể vẫn cần đo tín hiệu trên mạch.
