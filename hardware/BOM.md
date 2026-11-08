# Danh sách đầy đủ linh kiện trên mạch

Phương án lắp: AT89S52 dùng IC rời có đế; ESP32, OLED và TXS0108E là module cắm header. Mọi đế/header trong bảng đều được hàn lên PCB. IC/module cắm vào sau khi kiểm tra nguồn. Không cộng lại những linh kiện đã có sẵn bên trong module.

Giá tham khảo ngày **01/11/2026**, đơn vị VND. Bảng đầu ghi **đơn giá một linh kiện và thành tiền theo số lượng lắp**; bảng mua theo gói ở dưới ghi tiền cần trả khi mua mới. Đơn giá trở/LED/nút/header được quy đổi từ gói/thanh, không phải xác nhận shop bán lẻ từng chiếc.

| Ký hiệu | SL lắp | Linh kiện | Đơn giá/chi tiết | Thành tiền lắp | Kiểu lắp | Vị trí / lưu ý |
|---|---:|---|---:|---:|---|---|
| U1 | 1 | [AT89S52-24PU](https://chotroihn.vn/at89s52-24pu-dip40) | 27.000đ | 27.000đ | DIP-40 | Bộ xử lý đo/hiển thị; nguồn 5 V. Giá: 1 IC DIP40; RSCH-20261101-0011; shop khác có giá 79.000đ |
| U2 | 1 | [ESP32-C3 SuperMini](https://icdayroi.com/kit-phat-trien-wifi-bluetooth-esp32-c3-super-mini-4mb) | 75.000đ | 75.000đ | 16 chân, 2 hàng 1x8 | Board ESP32-C3 SuperMini; xác minh footprint và nhãn GPIO trước khi làm PCB. Giá: 1 board; RSCH-20261101-0009 |
| U4 | 1 | [Module TXS0108E 8 kênh](https://icdayroi.com/txs0108e-8-kenh-chuyen-muc-logic-1-8v-3-3v-5v) | 15.000đ | 15.000đ | Module 2 hàng, đối chiếu footprint | A=3,3 V; B=5 V; bốn kênh I²C/UART; OE từ ESP32 GPIO6. Giá: 1 module; RSCH-20261101-0009 |
| U5 | 1 | [DHT11 cảm biến rời](https://chotroihn.vn/cam-bien-nhiet-do-do-am-dht11) | 25.000đ | 25.000đ | 4 chân | VCC/DATA/NC/GND; không nhầm pin module 3 chân. Giá: 1 cảm biến; RSCH-20261101-0009 |
| U6 | 1 | [OLED trắng 0,96 inch SSD1315 I²C 128x64](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c) | 65.000đ | 65.000đ | Module 4 chân | Module Hshop đã chọn; cấp 3,3 V, kiểm tra thứ tự chân in trên module. Giá: 1 màn hình; RSCH-20261101-0009 |
| Y1 | 1 | [Thạch anh 11,0592 MHz](https://icdayroi.com/thach-anh-11-0592mhz-hc49-dip) | 1.500đ | 1.500đ | HC-49S | Dao động 11,0592 MHz cho UART 9600; đối chiếu điện dung tải. Giá: 1 thạch anh; RSCH-20261101-0011 |
| R1,R3,R7 | 3 | [10 kΩ 1% 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 360đ | Axial THT | R1 kéo RST chân 9 xuống GND; R3 kéo nút trang lên 5 V; R7 base-emitter Q1 giữ Q1 tắt. Giá: Mua gói 50, dùng 3; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| R6 | 1 | 3,3 kΩ 0,25 W | Chưa xác nhận | Chưa xác nhận | Axial THT | Kéo nút base Q1 lên 5 V; P2.0 kéo xuống ~1,5 mA để tắt relay. Giá: Chưa khảo sát giá |
| R2 | 1 | [4,7 kΩ 1% 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 120đ | Axial THT | Kéo DATA DHT11 lên 5 V. Giá: Mua gói 50, dùng 1 |
| R4 | 1 | [100 kΩ 1% 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 120đ | Axial THT | Kéo OE TXS0108E xuống GND khi ESP32 khởi động; bỏ pull-up OE trên module nếu có. Giá: Mua gói 50, dùng 1; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| R10,R5 | 2 | [1 kΩ 0,25 W](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 120đ | 240đ | Axial THT | R10 hạn dòng LED nguồn; R5 nối tiếp base Q1. Giá: Mua gói 50, dùng 2 |
| C1,C3,C5,C6,C16 | 5 | [100 nF X7R ≥16 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 2.500đ | THT 2,54 mm | VCC AT89S52, TXS VCCB 5V, OLED 3V3, ESP32 5V, đầu ra LM7805; đặt sát tải. Giá: Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| C14 | 1 | 100 µF ≥25 V | Chưa xác nhận | Chưa xác nhận | Tụ hóa radial | Đầu vào LM7805 sau D2; đúng cực. Giá: Chưa khảo sát giá |
| C15 | 1 | 330 nF ≥25 V | Chưa xác nhận | Chưa xác nhận | Tụ gốm THT | Sát chân IN LM7805 theo datasheet. Giá: Chưa khảo sát giá |
| C7 | 1 | [470 µF ≥10 V](https://chotroihn.vn/tu-hoa-10v) | 1.000đ | 1.000đ | Tụ hóa radial | Tụ nguồn 5 V gần ESP32; đúng cực. Giá: 1 tụ |
| C8 | 1 | [10 µF ≥10 V](https://chotroihn.vn/tu-hoa-16v) | 1.000đ | 1.000đ | Tụ hóa radial | Lọc nhánh 3,3 V OLED; đúng cực. Giá: 3 tụ 10uF 16V; C2 reset, C8/C11 lọc nguồn; kiểm tra cực tính |
| C9,C10 | 2 | [22 pF C0G/NP0 ≥25 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 1.000đ | Tụ gốm THT | Hai tụ Y1; giá trị khởi đầu, đối chiếu CL thạch anh trước khi chốt PCB. Giá: Giá biến thể 22P; xác nhận C0G/NP0 và tải thạch anh trước khi mua |
| C2,C11 | 2 | [10 µF ≥10 V](https://chotroihn.vn/tu-hoa-16v) | 1.000đ | 2.000đ | Tụ hóa radial | C11 lọc 5 V; C2 reset: cực + lên 5 V, cực - vào RST chân 9. Giá: 3 tụ 10uF 16V; C2 reset, C8/C11 lọc nguồn; kiểm tra cực tính |
| C12 | 1 | [100 nF X7R ≥16 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 500đ | THT 2,54 mm | Lọc nguồn sát VCC/GND DHT11. Giá: Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| C13 | 1 | [100 nF X7R ≥16 V](https://chotroihn.vn/tu-gom-vang-50v) | 500đ | 500đ | THT 2,54 mm | Lọc VCCA 3,3 V của TXS0108E sát module. Giá: Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| D1 | 1 | [LED xanh 3 mm](https://chotroihn.vn/goi-100-con-led-duc-3mm) | 290đ | 290đ | THT | LED báo có nguồn 5 V. Giá: Mua gói 100, dùng 1 |
| U7 | 1 | LM7805 ổn áp 5 V 1,5 A | Chưa xác nhận | Chưa xác nhận | TO-220 nằm ngang, vít xuống PCB | Tab = GND: vít M3 xuống vùng đồng GND hai mặt; với 12 V tỏa ~1,6 W, cần vùng đồng lớn hoặc tản phụ. Giá: Chưa khảo sát giá |
| D2 | 1 | SR360 Schottky 3 A 60 V | Chưa xác nhận | Chưa xác nhận | DO-201AD | Chống cắm ngược cực nguồn 12 V, sụt áp ~0,5 V; nối tiếp trước LM7805. Giá: Chưa khảo sát giá |
| SW1,SW2 | 2 | [Nút nhấn thường hở](https://chotroihn.vn/bo-10-nut-nhan-4-chan) | 500đ | 1.000đ | Tactile 6x6 mm | SW1 đổi trang; SW2 reset AT89S52. Giá: Mua gói 10, dùng 2 |
| J1 | 1 | Jack DC 5,5x2,1 mm hàn mạch | Chưa xác nhận | Chưa xác nhận | DC-005, 3 chân | Tâm dương; chân switch để trống. Giá: Chưa khảo sát giá |
| J7 | 1 | Domino 2 chân 5,08 mm | Chưa xác nhận | Chưa xác nhận | Pitch 5,08 mm | Đầu vào 12 V song song jack J1: chân 1 (+), chân 2 GND; chỉ cấp một nguồn. Giá: Chưa khảo sát giá |
| J2A,J2B | 2 | [Header cái 1x8](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 400đ | 800đ | Pitch 2,54 mm | Đế cắm ESP32; đo khoảng cách hai hàng của board thực tế. Giá: 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| J4 | 1 | [Header cái 1x4](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 200đ | 200đ | Pitch 2,54 mm | Đế cắm OLED. Giá: 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| J3 | 1 | [Header ISP AT89S52 1x6](https://chotroihn.vn/jump-duc-don-1x40p-2-54) | 300đ | 300đ | Pitch 2,54 mm | RST/VCC/GND/MISO/SCK/MOSI; nạp chính bằng Burn-E ngoài mạch. Giá: 1 thanh 40 chân, dùng 6 chân ISP AT89S52; giả định chân đực module đi kèm module |
| J5A,J5B | 2 | [Header cái 1x10 cho module TXS0108E](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 500đ | 1.000đ | Pitch 2,54 mm, xác minh hàng mua | Hàn đế module; chỉnh số chân/footprint nếu module thực tế khác. Giá: 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| J6 | 1 | Domino 2 chân 5,08 mm | Chưa xác nhận | Chưa xác nhận | Pitch 5,08 mm | COM/NC của relay K1 (NO bỏ trống); tải có điện khi relay tắt; chỉ tải điện áp thấp. Giá: Chưa khảo sát giá |
| K1 | 1 | Relay SRD-05VDC-SL-C | Chưa xác nhận | Chưa xác nhận | Hàn PCB, SPDT | Cuộn 5 V ~70 mA; chân 2/5 cuộn, 1 COM, 3 NO, 4 NC. Giá: Chưa khảo sát giá |
| Q1 | 1 | 2SC1815-GR NPN | Chưa xác nhận | Chưa xác nhận | TO-92 E-C-B | Đóng phía GND cuộn relay; P2.0 mức cao = relay bật (firmware v0.2.0). Giá: Chưa khảo sát giá |
| D3 | 1 | 1N4007 | Chưa xác nhận | Chưa xác nhận | DO-41 | Điốt dập xung ngược song song cuộn relay. Giá: Chưa khảo sát giá |
| SK1 | 1 | [Đế IC DIP-40](https://chotroihn.vn/de-ic) | 1.500đ | 1.500đ | Wide 15,24 mm | Đế AT89S52, hàn đế rồi cắm IC. Giá: Biến thể 40 chân; xác nhận loại rộng cho AT89S52 DIP40 |
| TP1,TP2,TP3 | 3 | Test point vòng dây | 0đ | 0đ | THT | Đo 5 V / 3,3 V / GND. Giá: Tận dụng chân/dây cắt thừa của header đã tính; không mua thêm |

**Tổng số chi tiết trong bảng:** 50 (bao gồm IC/module/đế; không gồm PCB và vật tư ngoài mạch).

**Giá trị linh kiện dùng trên một mạch: 222.930đ, chưa gồm mục chưa có giá.**

## Tiền mua thực tế theo gói/thanh

| Mục | Số đơn vị/gói mua | Giá mỗi đơn vị/gói | Thành tiền mua | Quy cách / ghi chú |
|---|---:|---:|---:|---|
| [U1: AT89S52 DIP-40](https://chotroihn.vn/at89s52-24pu-dip40) | 1 | 27.000đ | 27.000đ | 1 IC DIP40; RSCH-20261101-0011; shop khác có giá 79.000đ |
| [U2: ESP32-C3 SuperMini 4MB](https://icdayroi.com/kit-phat-trien-wifi-bluetooth-esp32-c3-super-mini-4mb) | 1 | 75.000đ | 75.000đ | 1 board; RSCH-20261101-0009 |
| [U4: Module TXS0108E](https://icdayroi.com/txs0108e-8-kenh-chuyen-muc-logic-1-8v-3-3v-5v) | 1 | 15.000đ | 15.000đ | 1 module; RSCH-20261101-0009 |
| [U5: DHT11 rời 4 chân](https://chotroihn.vn/cam-bien-nhiet-do-do-am-dht11) | 1 | 25.000đ | 25.000đ | 1 cảm biến; RSCH-20261101-0009 |
| [U6: OLED SSD1315 0,96 inch](https://hshop.vn/lcd-oled-trang-0-96-inch-i2c) | 1 | 65.000đ | 65.000đ | 1 màn hình; RSCH-20261101-0009 |
| [Y1: Thạch anh 11.0592MHz HC49 DIP](https://icdayroi.com/thach-anh-11-0592mhz-hc49-dip) | 1 | 1.500đ | 1.500đ | 1 thạch anh; RSCH-20261101-0011 |
| [R1,R3,R7: Điện trở 10kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 3; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| [R2: Điện trở 4,7kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1 |
| [R4: Điện trở 100kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 1; trang báo hết hàng biến thể này; cần xác nhận nguồn khác |
| [R10,R5: Điện trở 1kΩ 1/4W 1%](https://chotroihn.vn/tro-vach-1-4w-1-50c) | 1 | 6.000đ | 6.000đ | Mua gói 50, dùng 2 |
| [C1,C3,C5,C6,C12,C13,C16: Tụ gốm 100nF](https://chotroihn.vn/tu-gom-vang-50v) | 7 | 500đ | 3.500đ | Giá biến thể 0.1uF/104; đối chiếu điện môi X7R theo BOM trước khi mua |
| [C7: Tụ hóa 470uF 10V](https://chotroihn.vn/tu-hoa-10v) | 1 | 1.000đ | 1.000đ | 1 tụ |
| [C2,C8,C11: Tụ hóa 10uF 16V](https://chotroihn.vn/tu-hoa-16v) | 3 | 1.000đ | 3.000đ | 3 tụ 10uF 16V; C2 reset, C8/C11 lọc nguồn; kiểm tra cực tính |
| [C9,C10: Tụ gốm 22pF](https://chotroihn.vn/tu-gom-vang-50v) | 2 | 500đ | 1.000đ | Giá biến thể 22P; xác nhận C0G/NP0 và tải thạch anh trước khi mua |
| [D1: LED xanh lá 3mm](https://chotroihn.vn/goi-100-con-led-duc-3mm) | 1 | 29.000đ | 29.000đ | Mua gói 100, dùng 1 |
| U7: LM7805 TO-220 | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| D2: Diode Schottky SR360 DO-201AD | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| D3: Diode 1N4007 | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| Q1: Transistor 2SC1815-GR TO-92 | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| R6: Điện trở 3.3kΩ 1/4W | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| C14: Tụ hóa 100uF 25V | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| C15: Tụ gốm 330nF | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| [SW1,SW2: Nút nhấn 6x6](https://chotroihn.vn/bo-10-nut-nhan-4-chan) | 1 | 5.000đ | 5.000đ | Mua gói 10, dùng 2 |
| J1: Jack DC 5.5x2.1 hàn mạch | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| J7: Domino 2 chân 5.08mm | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| [J2A,J2B,J4,J5A,J5B: Header cái 2,54mm](https://chotroihn.vn/jump-cai-don-1-40p-2-54) | 2 | 2.000đ | 4.000đ | 2 thanh 40 chân để cắt 8+8+4+10+10; chừa hao hụt khi cắt |
| [J3: Header đực 2,54mm](https://chotroihn.vn/jump-duc-don-1x40p-2-54) | 1 | 2.000đ | 2.000đ | 1 thanh 40 chân, dùng 6 chân ISP AT89S52; giả định chân đực module đi kèm module |
| K1: Relay SRD-05VDC-SL-C | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| J6: Domino 2 chân 5.08mm | 1 | Chưa xác nhận | Chưa xác nhận | Chưa khảo sát giá |
| [SK1: Đế IC 40 chân](https://chotroihn.vn/de-ic) | 1 | 1.500đ | 1.500đ | Biến thể 40 chân; xác nhận loại rộng cho AT89S52 DIP40 |
| TP1,TP2,TP3: Test point tự làm | 0 | 0đ | 0đ | Tận dụng chân/dây cắt thừa của header đã tính; không mua thêm |
| PCB: In PCB theo giá người dùng | 1 | 120.000đ | 120.000đ | Giá người dùng cung cấp, không phải giá nhà sản xuất đã khảo sát |

- Linh kiện mua mới theo gói/thanh: **282.500đ**, chưa gồm mục chưa có giá.
- In PCB theo giá người dùng: **120.000đ**.
- **Tổng tiền mua + PCB: 402.500đ, chưa gồm mục chưa có giá.**
- Nếu chỉ phân bổ lượng linh kiện dùng trên một PCB: **342.930đ**, chưa gồm mục chưa có giá. Phần chênh lệch là linh kiện dư từ gói/thanh mua.
- J1, J6, J7, U7, D2, D3, Q1, R6, C14, C15 và K1 chưa khảo sát giá, để trống trong CSV; không tính thành 0đ. Giá tụ tham khảo cần xác nhận đúng điện môi; trở 10kΩ/100kΩ ở nguồn giá đang báo hết hàng.
- Chưa gồm vận chuyển, adapter/cáp, vỏ, thiếc/flux và công hàn. Burn-E đã có nên không mua lại.

## Vật tư đi kèm, không hàn trực tiếp

- 1 adapter DC 12 V / 1 A, jack 5,5x2,1 mm tâm dương (hoặc đấu dây vào domino J7); dây USB lập trình ESP32.
- 1 PCB theo kích thước thực tế ESP32/OLED; thiếc, flux và dây nối cho bản thử.
- Mạch nạp Burn-E đang sử dụng, cáp USB và phần mềm đúng phiên bản để nạp/verify HEX AT89S52; đây là dụng cụ dùng lại, không hàn lên mạch.

## Điều kiện mua/lắp

- Nguồn giá chi tiết và quy cách mua nằm ngay trong hai bảng trên; ledger RSCH-20261101-0009/0010/0011. Không đặt PCB chỉ dựa vào sơ đồ luồng: cần schematic/netlist và kiểm tra footprint.
- TXS0108E có pull-up nội. Không lắp thêm bốn điện trở 4,7 kΩ kéo bus như thiết kế cũ; kiểm tra pull-up có sẵn trên OLED/module và đo dạng sóng.
- OE nối GPIO6 và R4 100 kΩ xuống GND; không để module kéo cứng OE lên nguồn. Phải kiểm tra/tháo cầu nối hoặc pull-up OE nếu module đã gắn.
- Chọn ESP32-C3 SuperMini đã hàn chân đực. Nếu hàng mua chưa có chân, bổ sung 2 thanh header đực 1x8; không tính trùng với header có sẵn.
- Không cắm USB ESP32 khi đang cấp nguồn jack nếu board không có bảo vệ chống cấp ngược. Không nối adapter vào chân 5V/3V3.
- Giá trị/điện áp từng linh kiện là cấu hình thiết kế; xác minh nguồn và dạng sóng trên mạch thật trước khi vận hành.
