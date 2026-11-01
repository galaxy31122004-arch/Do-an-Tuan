# Danh sách đầy đủ linh kiện trên mạch

Phương án lắp: PIC dùng IC rời có đế; ESP32, OLED và TXS0108E là module cắm header. Mọi đế/header trong bảng đều được hàn lên PCB. IC/module cắm vào sau khi kiểm tra nguồn. Không cộng lại những linh kiện đã có sẵn bên trong module.

Giá tham khảo ngày **01/11/2026**, đơn vị VND. Bảng đầu ghi **đơn giá một linh kiện và thành tiền theo số lượng lắp**; bảng mua theo gói ở dưới ghi tiền cần trả khi mua mới. Đơn giá trở/LED/nút/header được quy đổi từ gói/thanh, không phải xác nhận shop bán lẻ từng chiếc.

| Ký hiệu | SL lắp | Linh kiện | Đơn giá/chi tiết | Thành tiền lắp | Kiểu lắp | Vị trí / lưu ý |
|---|---:|---|---:|---:|---|---|
| U1 | 1 | [PIC16F877A-I/P](https://chotroihn.vn/pic-16f877a-ip-dip40) | 129.000đ | 129.000đ | DIP-40 | Bộ xử lý đo/hiển thị; nguồn 5 V. Giá: 1 IC; RSCH-20261101-0009 |
| U2 | 1 | [ESP32-C3 SuperMini](https://icdayroi.com/kit-phat-trien-wifi-bluetooth-esp32-c3-super-mini-4mb) | 75.000đ | 75.000đ | 16 chân, 2 hàng 1x8 | Board ESP32-C3 SuperMini; xác minh footprint và nhãn GPIO trước khi làm PCB. Giá: 1 board; RSCH-20261101-0009 |
| U4 | 1 | [Module TXS0108E 8 kênh](https://icdayroi.com/txs0108e-8-kenh-chuyen-muc-logic-1-8v-3-3v-5v) | 15.000đ | 15.000đ | Module 2 hàng, đối chiếu footprint | A=3,3 V; B=5 V; bốn kênh I²C/UART; OE từ ESP32 GPIO6. Giá: 1 module; RSCH-20261101-0009 |
| U5 | 1 | [DHT11 cảm biến rời](https://chotroihn.vn/cam-bien-nhiet-do-do-am-dht11) | 25.000đ | 25.000đ | 4 chân | VCC/DATA/NC/GND; không nhầm pin module 3 chân. Giá: 1 cảm biến; RSCH-20261101-0009 |
| U6 | 1 | [OLED trắng 0,96 inch SSD1315 I²C 128x64](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c) | 65.000đ | 65.000đ | Module 4 chân | Module Hshop đã chọn; cấp 3,3 V, kiểm tra thứ tự chân in trên module. Giá: 1 màn hình; RSCH-20261101-0009 |
| Y1 | 1 | [Thạch anh 20 MHz](https://icdayroi.com/thach-anh-20mhz-hc49-dip) | 1.500đ | 1.500đ | HC-49S | Dao động PIC; chọn loại phù hợp HS, đối chiếu điện dung tải. Giá: 1 thạch anh; RSCH-20261101-0010 |
| R1,R3 | 2 | [10 kΩ 1% 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 240đ | Axial THT | R1 kéo MCLR lên 5 V; R3 kéo nút trang lên 5 V. Giá: Mua gói 50, dùng 2; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| R2 | 1 | [4,7 kΩ 1% 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 120đ | Axial THT | Kéo DATA DHT11 lên 5 V. Giá: Mua gói 50, dùng 1 |
| R4 | 1 | [100 kΩ 1% 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 120đ | Axial THT | Kéo OE TXS0108E xuống GND khi ESP32 khởi động; bỏ pull-up OE trên module nếu có. Giá: Mua gói 50, dùng 1; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| R10 | 1 | [1 kΩ 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 120đ | Axial THT | Hạn dòng LED nguồn. Giá: Mua gói 50, dùng 1 |
| C1,C2,C3,C5,C6 | 5 | [100 nF X7R ≥16 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 2.500đ | THT 2,54 mm | Hai cặp VDD PIC, TXS VCCB 5V, OLED 3V3, ESP32 5V; đặt sát tải. Giá: Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| C7 | 1 | [470 µF ≥10 V](https://chotroihn.vn/tu-hoa-10v) | 1.000đ | 1.000đ | Tụ hóa radial | Tụ nguồn 5 V gần ESP32; đúng cực. Giá: 1 tụ |
| C8 | 1 | [10 µF ≥10 V](https://chotroihn.vn/tu-hoa-16v) | 1.000đ | 1.000đ | Tụ hóa radial | Lọc nhánh 3,3 V OLED; đúng cực. Giá: 2 tụ; điện áp cao hơn tối thiểu 10V của BOM |
| C9,C10 | 2 | [22 pF C0G/NP0 ≥25 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 1.000đ | Tụ gốm THT | Hai tụ Y1; giá trị khởi đầu, đối chiếu CL thạch anh trước khi chốt PCB. Giá: Giá biến thể 22P; xác nhận C0G/NP0 và tải thạch anh trước khi mua |
| C11 | 1 | [10 µF ≥10 V](https://chotroihn.vn/tu-hoa-16v) | 1.000đ | 1.000đ | Tụ hóa radial | Lọc nhánh 5 V PIC; đúng cực. Giá: 2 tụ; điện áp cao hơn tối thiểu 10V của BOM |
| C12 | 1 | [100 nF X7R ≥16 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 500đ | THT 2,54 mm | Lọc nguồn sát VCC/GND DHT11. Giá: Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| C13 | 1 | [100 nF X7R ≥16 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 500đ | THT 2,54 mm | Lọc VCCA 3,3 V của TXS0108E sát module. Giá: Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| D1 | 1 | [LED xanh 3 mm](https://chotroihn.vn/goi-100-con-led-duc-3mm) | 290đ | 290đ | THT | LED báo có nguồn 5 V. Giá: Mua gói 100, dùng 1 |
| F1 | 1 | Cầu chì tự phục hồi Ihold 1 A ≥6 V | Chưa xác nhận | Chưa xác nhận | Radial THT | Mắc nối tiếp đầu vào 5 V; đối chiếu dòng khởi động thực tế. Giá: Chưa có giá hợp lệ đúng quy cách. Không dùng giá giữ chỗ 0/1đ hoặc thay bằng SMD1.1A trong tổng |
| SW1,SW2 | 2 | [Nút nhấn thường hở](https://chotroihn.vn/bo-10-nut-nhan-4-chan) | 500đ | 1.000đ | Tactile 6x6 mm | SW1 đổi trang; SW2 reset PIC. Giá: Mua gói 10, dùng 2 |
| J1 | 1 | [Terminal cấp nguồn 2 chân](https://chotroihn.vn/terminal-kf301-300v-15a) | 1.500đ | 1.500đ | Pitch 5,08 mm | Đầu vào 5 V và GND; ghi rõ cực tính. Giá: 1 terminal |
| J2A,J2B | 2 | [Header cái 1x8](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 400đ | 800đ | Pitch 2,54 mm | Đế cắm ESP32; đo khoảng cách hai hàng của board thực tế. Giá: 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| J4 | 1 | [Header cái 1x4](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 200đ | 200đ | Pitch 2,54 mm | Đế cắm OLED. Giá: 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| J3 | 1 | [Header dịch vụ ICSP 1x6](https://chotroihn.vn/jump-duc-don-1x40p-2-54) | 300đ | 300đ | Pitch 2,54 mm | VPP/VDD/GND/PGD/PGC/NC; nạp chính bằng Burn-E ngoài mạch. Giá: 1 thanh 40 chân, dùng 6 chân ICSP; giả định chân đực module đi kèm module |
| J5A,J5B | 2 | [Header cái 1x10 cho module TXS0108E](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 500đ | 1.000đ | Pitch 2,54 mm, xác minh hàng mua | Hàn đế module; chỉnh số chân/footprint nếu module thực tế khác. Giá: 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| SK1 | 1 | [Đế IC DIP-40](https://chotroihn.vn/de-ic) | 1.500đ | 1.500đ | Wide 15,24 mm | Đế PIC, hàn đế rồi cắm IC. Giá: Biến thể 40 chân; xác nhận loại rộng cho PIC DIP40 |
| TP1,TP2,TP3 | 3 | Test point vòng dây | 0đ | 0đ | THT | Đo 5 V / 3,3 V / GND. Giá: Tận dụng chân/dây cắt thừa của header đã tính; không mua thêm |

**Tổng số chi tiết trong bảng:** 38 (bao gồm IC/module/đế; không gồm PCB và vật tư ngoài mạch).

**Giá trị linh kiện dùng trên một mạch: 325.190đ, chưa gồm F1.**

## Tiền mua thực tế theo gói/thanh

| Mục | Số đơn vị/gói mua | Giá mỗi đơn vị/gói | Thành tiền mua | Quy cách / ghi chú |
|---|---:|---:|---:|---|
| [U1: PIC16F877A DIP-40](https://chotroihn.vn/pic-16f877a-ip-dip40) | 1 | 129.000đ | 129.000đ | 1 IC; RSCH-20261101-0009 |
| [U2: ESP32-C3 SuperMini 4MB](https://icdayroi.com/kit-phat-trien-wifi-bluetooth-esp32-c3-super-mini-4mb) | 1 | 75.000đ | 75.000đ | 1 board; RSCH-20261101-0009 |
| [U4: Module TXS0108E](https://icdayroi.com/txs0108e-8-kenh-chuyen-muc-logic-1-8v-3-3v-5v) | 1 | 15.000đ | 15.000đ | 1 module; RSCH-20261101-0009 |
| [U5: DHT11 rời 4 chân](https://chotroihn.vn/cam-bien-nhiet-do-do-am-dht11) | 1 | 25.000đ | 25.000đ | 1 cảm biến; RSCH-20261101-0009 |
| [U6: OLED SSD1315 0,96 inch](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c) | 1 | 65.000đ | 65.000đ | 1 màn hình; RSCH-20261101-0009 |
| [Y1: Thạch anh 20MHz HC49 DIP](https://icdayroi.com/thach-anh-20mhz-hc49-dip) | 1 | 1.500đ | 1.500đ | 1 thạch anh; RSCH-20261101-0010 |
| [R1,R3: Điện trở 10kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 2; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| [R2: Điện trở 4,7kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1 |
| [R4: Điện trở 100kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| [R10: Điện trở 1kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1 |
| [C1,C2,C3,C5,C6,C12,C13: Tụ gốm 100nF](https://chotroihn.vn/tu-gom-vang-50v) | 7 | 500đ | 3.500đ | Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| [C7: Tụ hóa 470uF 10V](https://chotroihn.vn/tu-hoa-10v) | 1 | 1.000đ | 1.000đ | 1 tụ |
| [C8,C11: Tụ hóa 10uF 16V](https://chotroihn.vn/tu-hoa-16v) | 2 | 1.000đ | 2.000đ | 2 tụ; điện áp cao hơn tối thiểu 10V của BOM |
| [C9,C10: Tụ gốm 22pF](https://chotroihn.vn/tu-gom-vang-50v) | 2 | 500đ | 1.000đ | Giá biến thể 22P; xác nhận C0G/NP0 và tải thạch anh trước khi mua |
| [D1: LED xanh lá 3mm](https://chotroihn.vn/goi-100-con-led-duc-3mm) | 1 | 29.000đ | 29.000đ | Mua gói 100, dùng 1 |
| F1: Cầu chì PTC radial Ihold 1A | 1 | Chưa xác nhận | Chưa xác nhận | Chưa có giá hợp lệ đúng quy cách. Không dùng giá giữ chỗ 0/1đ hoặc thay bằng SMD1.1A trong tổng |
| [SW1,SW2: Nút nhấn 6x6](https://chotroihn.vn/bo-10-nut-nhan-4-chan) | 1 | 5.000đ | 5.000đ | Mua gói 10, dùng 2 |
| [J1: Terminal KF301 2 chân](https://chotroihn.vn/terminal-kf301-300v-15a) | 1 | 1.500đ | 1.500đ | 1 terminal |
| [J2A,J2B,J4,J5A,J5B: Header cái 2,54mm](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 2 | 2.000đ | 4.000đ | 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| [J3: Header đực 2,54mm](https://chotroihn.vn/jump-duc-don-1x40p-2-54) | 1 | 2.000đ | 2.000đ | 1 thanh 40 chân, dùng 6 chân ICSP; giả định chân đực module đi kèm module |
| [SK1: Đế IC 40 chân](https://chotroihn.vn/de-ic) | 1 | 1.500đ | 1.500đ | Biến thể 40 chân; xác nhận loại rộng cho PIC DIP40 |
| TP1,TP2,TP3: Test point tự làm | 0 | 0đ | 0đ | Tận dụng chân/dây cắt thừa của header đã tính; không mua thêm |
| PCB: In PCB theo giá người dùng | 1 | 120.000đ | 120.000đ | Giá người dùng cung cấp, không phải giá nhà sản xuất đã khảo sát |

- Linh kiện mua mới theo gói/thanh: **385.000đ**, chưa gồm F1.
- In PCB theo giá người dùng: **120.000đ**.
- **Tổng tiền mua + PCB: 505.000đ, chưa gồm F1.**
- Nếu chỉ phân bổ lượng linh kiện dùng trên một PCB: **445.190đ**, chưa gồm F1. Phần chênh lệch là linh kiện dư từ gói/thanh mua.
- F1 chưa có giá đúng quy cách, để trống trong CSV; không tính thành 0đ. Giá tụ tham khảo cần xác nhận đúng điện môi; trở 10kΩ/100kΩ ở nguồn giá đang báo hết hàng.
- Chưa gồm vận chuyển, adapter/cáp, vỏ, thiếc/flux và công hàn. Burn-E đã có nên không mua lại.

## Vật tư đi kèm, không hàn trực tiếp

- 1 adapter DC 5 V / 2 A ổn áp, dây cấp nguồn và dây USB lập trình ESP32.
- 1 PCB theo kích thước thực tế ESP32/OLED; thiếc, flux và dây nối cho bản thử.
- Mạch nạp Burn-E đang sử dụng, cáp USB và phần mềm đúng phiên bản để nạp/verify HEX PIC16F877A; đây là dụng cụ dùng lại, không hàn lên mạch.

## Điều kiện mua/lắp

- Nguồn giá chi tiết và quy cách mua nằm ngay trong hai bảng trên; ledger RSCH-20261101-0009/0010. Không đặt PCB chỉ dựa vào sơ đồ luồng: cần schematic/netlist và kiểm tra footprint.
- TXS0108E có pull-up nội. Không lắp thêm bốn điện trở 4,7 kΩ kéo bus như thiết kế cũ; kiểm tra pull-up có sẵn trên OLED/module và đo dạng sóng.
- OE nối GPIO6 và R4 100 kΩ xuống GND; không để module kéo cứng OE lên nguồn. Phải kiểm tra/tháo cầu nối hoặc pull-up OE nếu module đã gắn.
- Chọn ESP32-C3 SuperMini đã hàn chân đực. Nếu hàng mua chưa có chân, bổ sung 2 thanh header đực 1x8; không tính trùng với header có sẵn.
- Chỉ dùng một nguồn cấp 5 V: tháo nguồn ngoài khi cắm USB nếu board không có bảo vệ chống cấp ngược. Không nối adapter vào chân 3V3.
- Giá trị/điện áp từng linh kiện là cấu hình thiết kế; xác minh nguồn và dạng sóng trên mạch thật trước khi vận hành.
