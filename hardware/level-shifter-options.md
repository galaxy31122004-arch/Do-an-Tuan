# Vì sao có BSS138? Có thể thay TXS0108E không?

Thiết kế hiện tại tách hai rail logic: PIC/DS1307 5 V và OLED/ESP32 3,3 V. BSS138 chuyển hai đường open-drain SDA/SCL giữa hai rail; điện trở ở mỗi phía kéo đường lên đúng nguồn của phía đó. Nguồn OLED được seller ghi 3,3–5 V không tự chứng minh chân SDA/SCL chịu được pull-up 5 V.

**Có thể dùng một module TXS0108E thay các khối chuyển mức hiện tại.** TI công bố hỗ trợ open-drain và push-pull, VCCA 1,4–3,6 V, VCCB 1,65–5,5 V và VCCA ≤ VCCB. Với mạch này: A=3,3 V, B=5 V. Module cần dây ngắn, nguồn lọc tốt và OE điều khiển đúng mức VCCA. Chưa đổi BOM mặc định vì người dùng đang hỏi lý do, chưa chọn thay phương án.

## Ánh xạ thay thế

| Kênh TXS0108E | Phía A (3,3 V) | Phía B (5 V) |
|---|---|---|
| A1/B1 | OLED SDA | PIC RC4 chân 23 + DS1307 SDA chân 5 |
| A2/B2 | OLED SCL | PIC RC3 chân 18 + DS1307 SCL chân 6 |
| A3/B3 | ESP32 GPIO16 RX | PIC RC6 TX chân 25 |
| A4/B4 | ESP32 GPIO17 TX | PIC RC7 RX chân 26 |

GND module nối GND chung; VCCA=3,3 V; VCCB=5 V. OE tham chiếu VCCA: giữ thấp khi khởi động theo hướng dẫn TI rồi đưa lên 3,3 V để bật; không cấp 5 V vào OE. Cách kéo/điều khiển OE, tụ lọc và pull-up phải đối chiếu schematic module cụ thể trước khi chốt. Không nối thêm mạch chia áp vào đường đã qua TXS.

Nếu đổi: bỏ Q1/Q2, U4/SK3 và R4/R5; rà soát R6–R9 vì TXS/module có cơ chế kéo lên bên trong. Không tự lắp thêm mọi pull-up 4,7k như phương án BSS138. Thêm module, header và tụ nguồn phù hợp footprint thực tế. Chân UART/I²C trong firmware giữ nguyên; nếu OE điều khiển bằng GPIO thì bổ sung cấu hình tương ứng.

Nguồn chính thức: [TI TXS0108E](https://www.ti.com/product/TXS0108E), datasheet trên cùng trang. Thông số hãng đã đọc ngày 2026-11-01 (RSCH-20261101-0005). Việc chuyển module cụ thể vẫn cần đo tín hiệu trên mạch.
