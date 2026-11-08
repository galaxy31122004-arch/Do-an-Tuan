"""One hardware source for the purchasing BOM and labelled wiring overview."""
import csv
import html
from pathlib import Path

ROOT=Path(__file__).resolve().parent
PARTS=[
('U1',1,'AT89S52-24PU','DIP-40','Bộ xử lý đo/hiển thị; nguồn 5 V'),
('U2',1,'ESP32-C3 SuperMini','16 chân, 2 hàng 1x8','Board ESP32-C3 SuperMini; xác minh footprint và nhãn GPIO trước khi làm PCB'),
('U4',1,'Module TXS0108E 8 kênh','Module 2 hàng, đối chiếu footprint','A=3,3 V; B=5 V; bốn kênh I²C/UART; OE từ ESP32 GPIO6'),
('U5',1,'DHT11 cảm biến rời','4 chân','VCC/DATA/NC/GND; không nhầm pin module 3 chân'),
('U6',1,'OLED trắng 0,96 inch SSD1315 I²C 128x64','Module 4 chân','Module Hshop đã chọn; cấp 3,3 V, kiểm tra thứ tự chân in trên module'),
('Y1',1,'Thạch anh 11,0592 MHz','HC-49S','Dao động 11,0592 MHz cho UART 9600; đối chiếu điện dung tải'),
('R1,R3,R6',3,'10 kΩ 1% 0,25 W','Axial THT','R1 kéo RST chân 9 xuống GND; R3 kéo nút trang lên 5 V; R6 kéo base Q1 lên 5 V để relay tắt chắc'),
('R2',1,'4,7 kΩ 1% 0,25 W','Axial THT','Kéo DATA DHT11 lên 5 V'),
('R4',1,'100 kΩ 1% 0,25 W','Axial THT','Kéo OE TXS0108E xuống GND khi ESP32 khởi động; bỏ pull-up OE trên module nếu có'),
('R10,R5',2,'1 kΩ 0,25 W','Axial THT','R10 hạn dòng LED nguồn; R5 trở base Q1 từ P2.0'),
('C1,C3,C5,C6,C16',5,'100 nF X7R ≥16 V','THT 2,54 mm','VCC AT89S52, TXS VCCB 5V, OLED 3V3, ESP32 5V, đầu ra LM7805; đặt sát tải'),
('C14',1,'100 µF ≥25 V','Tụ hóa radial','Đầu vào LM7805 sau D2; đúng cực'),
('C15',1,'330 nF ≥25 V','Tụ gốm THT','Sát chân IN LM7805 theo datasheet'),
('C7',1,'470 µF ≥10 V','Tụ hóa radial','Tụ nguồn 5 V gần ESP32; đúng cực'),
('C8',1,'10 µF ≥10 V','Tụ hóa radial','Lọc nhánh 3,3 V OLED; đúng cực'),
('C9,C10',2,'22 pF C0G/NP0 ≥25 V','Tụ gốm THT','Hai tụ Y1; giá trị khởi đầu, đối chiếu CL thạch anh trước khi chốt PCB'),
('C2,C11',2,'10 µF ≥10 V','Tụ hóa radial','C11 lọc 5 V; C2 reset: cực + lên 5 V, cực - vào RST chân 9'),
('C12',1,'100 nF X7R ≥16 V','THT 2,54 mm','Lọc nguồn sát VCC/GND DHT11'),
('C13',1,'100 nF X7R ≥16 V','THT 2,54 mm','Lọc VCCA 3,3 V của TXS0108E sát module'),
('D1',1,'LED xanh 3 mm','THT','LED báo có nguồn 5 V'),
('U7',1,'LM7805 ổn áp 5 V 1,5 A','TO-220 nằm ngang, vít xuống PCB','Tab = GND: vít M3 xuống vùng đồng GND hai mặt làm tản nhiệt; adapter 7,5–9 V để giảm nhiệt'),
('D2',1,'1N4007','DO-41','Chống cắm ngược cực jack DC, nối tiếp trước LM7805'),
('SW1,SW2',2,'Nút nhấn thường hở','Tactile 6x6 mm','SW1 đổi trang; SW2 reset AT89S52'),
('J1',1,'Jack DC 5,5x2,1 mm hàn mạch','DC-005, 3 chân','Tâm dương; chân switch để trống'),
('J2A,J2B',2,'Header cái 1x8','Pitch 2,54 mm','Đế cắm ESP32; đo khoảng cách hai hàng của board thực tế'),
('J4',1,'Header cái 1x4','Pitch 2,54 mm','Đế cắm OLED'),
('J3',1,'Header ISP AT89S52 1x6','Pitch 2,54 mm','RST/VCC/GND/MISO/SCK/MOSI; nạp chính bằng Burn-E ngoài mạch'),
('J5A,J5B',2,'Header cái 1x10 cho module TXS0108E','Pitch 2,54 mm, xác minh hàng mua','Hàn đế module; chỉnh số chân/footprint nếu module thực tế khác'),
('J6',1,'Domino 3 chân 5,08 mm','Pitch 5,08 mm','COM/NO/NC tiếp điểm relay K1; chỉ tải điện áp thấp'),
('K1',1,'Relay SRD-05VDC-SL-C','Hàn PCB, SPDT','Cuộn 5 V ~70 mA; chân 2/5 cuộn, 1 COM, 3 NO, 4 NC'),
('Q1',1,'S8550 PNP','TO-92 E-B-C','Đóng cuộn relay; P2.0 mức thấp = relay bật (firmware giữ nguyên)'),
('D3',1,'1N4007','DO-41','Điốt dập xung ngược song song cuộn relay'),
('SK1',1,'Đế IC DIP-40','Wide 15,24 mm','Đế AT89S52, hàn đế rồi cắm IC'),
('TP1,TP2,TP3',3,'Test point vòng dây','THT','Đo 5 V / 3,3 V / GND')
]

def main():
    # Retail quotes are maintained in the sourced purchasing sheet. Unit prices
    # below allocate pack/strip prices to the parts actually fitted on one PCB.
    with (ROOT/'cost-estimate.csv').open(encoding='utf-8-sig',newline='') as f:
        quotes=list(csv.DictReader(f))
    by_ref={ref:row for row in quotes for ref in row['Reference'].split(',')}
    def unit_price(ref):
        quote=by_ref[ref]
        if not quote['Price per purchase unit VND']: return None
        price=int(quote['Price per purchase unit VND'])
        if ref in {'R1','R2','R3','R4','R5','R6','R10'}: return price//50
        if ref=='D1': return price//100
        if ref in {'SW1','SW2'}: return price//10
        pins={'J2A':8,'J2B':8,'J4':4,'J5A':10,'J5B':10,'J3':6}
        if ref in pins: return price*pins[ref]//40
        return price
    def money(value):
        return 'Chưa xác nhận' if value is None else f'{value:,}'.replace(',','.')+'đ'
    expanded=[]
    for refs,quantity,part,package,note in PARTS:
        names=refs.split(',')
        prices=[unit_price(ref) for ref in names]
        assert all(price==prices[0] for price in prices), refs
        unit=prices[0];subtotal=None if unit is None else unit*quantity
        quote=by_ref[names[0]]
        expanded.append((refs,quantity,part,package,note,unit,subtotal,quote['Source'],quote['Note']))
    used_total=sum(row[6] for row in expanded if row[6] is not None)
    parts_purchase=sum(int(row['Subtotal VND']) for row in quotes if row['Reference']!='PCB' and row['Subtotal VND'])
    pcb=int(by_ref['PCB']['Subtotal VND'])
    with (ROOT/'BOM.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Reference','Quantity','Component','Package','Assembly note','Unit price VND','Fitted subtotal VND','Price source','Price basis / purchasing note'])
        for refs,quantity,part,package,note,unit,subtotal,source,basis in expanded:
            writer.writerow([refs,quantity,part,package,note,'' if unit is None else unit,'' if subtotal is None else subtotal,source,basis])
    lines=['# Danh sách đầy đủ linh kiện trên mạch','',
        'Phương án lắp: AT89S52 dùng IC rời có đế; ESP32, OLED và TXS0108E là module cắm header. Mọi đế/header trong bảng đều được hàn lên PCB. IC/module cắm vào sau khi kiểm tra nguồn. Không cộng lại những linh kiện đã có sẵn bên trong module.', '',
        'Giá tham khảo ngày **01/11/2026**, đơn vị VND. Bảng đầu ghi **đơn giá một linh kiện và thành tiền theo số lượng lắp**; bảng mua theo gói ở dưới ghi tiền cần trả khi mua mới. Đơn giá trở/LED/nút/header được quy đổi từ gói/thanh, không phải xác nhận shop bán lẻ từng chiếc.', '',
        '| Ký hiệu | SL lắp | Linh kiện | Đơn giá/chi tiết | Thành tiền lắp | Kiểu lắp | Vị trí / lưu ý |','|---|---:|---|---:|---:|---|---|']
    for refs,n,part,package,note,unit,subtotal,source,basis in expanded:
        label=f'[{part}]({source})' if source.startswith('http') else part
        lines.append(f'| {refs} | {n} | {label} | {money(unit)} | {money(subtotal)} | {package} | {note}. Giá: {basis} |')
    lines += ['',f'**Tổng số chi tiết trong bảng:** {sum(p[1] for p in PARTS)} (bao gồm IC/module/đế; không gồm PCB và vật tư ngoài mạch).',
        '',f'**Giá trị linh kiện dùng trên một mạch: {money(used_total)}, chưa gồm mục chưa có giá.**',
        '', '## Tiền mua thực tế theo gói/thanh', '',
        '| Mục | Số đơn vị/gói mua | Giá mỗi đơn vị/gói | Thành tiền mua | Quy cách / ghi chú |',
        '|---|---:|---:|---:|---|']
    for quote in quotes:
        price=None if not quote['Price per purchase unit VND'] else int(quote['Price per purchase unit VND'])
        subtotal=None if not quote['Subtotal VND'] else int(quote['Subtotal VND'])
        label=f"{quote['Reference']}: {quote['Item']}"
        if quote['Source'].startswith('http'):label=f"[{label}]({quote['Source']})"
        lines.append(f"| {label} | {quote['Purchase units/packs']} | {money(price)} | {money(subtotal)} | {quote['Note']} |")
    lines += ['',f'- Linh kiện mua mới theo gói/thanh: **{money(parts_purchase)}**, chưa gồm mục chưa có giá.',
        f'- In PCB theo giá người dùng: **{money(pcb)}**.',
        f'- **Tổng tiền mua + PCB: {money(parts_purchase+pcb)}, chưa gồm mục chưa có giá.**',
        f'- Nếu chỉ phân bổ lượng linh kiện dùng trên một PCB: **{money(used_total+pcb)}**, chưa gồm mục chưa có giá. Phần chênh lệch là linh kiện dư từ gói/thanh mua.',
        '- J1, J6, U7, D2, D3, Q1, C14, C15 và K1 chưa khảo sát giá, để trống trong CSV; không tính thành 0đ. Giá tụ tham khảo cần xác nhận đúng điện môi; trở 10kΩ/100kΩ ở nguồn giá đang báo hết hàng.',
        '- Chưa gồm vận chuyển, adapter/cáp, vỏ, thiếc/flux và công hàn. Burn-E đã có nên không mua lại.',
        '', '## Vật tư đi kèm, không hàn trực tiếp', '',
        '- 1 adapter DC 7,5–9 V / 1 A, jack 5,5x2,1 mm tâm dương; dây USB lập trình ESP32.',
        '- 1 PCB theo kích thước thực tế ESP32/OLED; thiếc, flux và dây nối cho bản thử.',
        '- Mạch nạp Burn-E đang sử dụng, cáp USB và phần mềm đúng phiên bản để nạp/verify HEX AT89S52; đây là dụng cụ dùng lại, không hàn lên mạch.',
        '', '## Điều kiện mua/lắp', '',
        '- Nguồn giá chi tiết và quy cách mua nằm ngay trong hai bảng trên; ledger RSCH-20261101-0009/0010/0011. Không đặt PCB chỉ dựa vào sơ đồ luồng: cần schematic/netlist và kiểm tra footprint.',
        '- TXS0108E có pull-up nội. Không lắp thêm bốn điện trở 4,7 kΩ kéo bus như thiết kế cũ; kiểm tra pull-up có sẵn trên OLED/module và đo dạng sóng.',
        '- OE nối GPIO6 và R4 100 kΩ xuống GND; không để module kéo cứng OE lên nguồn. Phải kiểm tra/tháo cầu nối hoặc pull-up OE nếu module đã gắn.',
        '- Chọn ESP32-C3 SuperMini đã hàn chân đực. Nếu hàng mua chưa có chân, bổ sung 2 thanh header đực 1x8; không tính trùng với header có sẵn.',
        '- Không cắm USB ESP32 khi đang cấp nguồn jack nếu board không có bảo vệ chống cấp ngược. Không nối adapter vào chân 5V/3V3.',
        '- Giá trị/điện áp từng linh kiện là cấu hình thiết kế; xác minh nguồn và dạng sóng trên mạch thật trước khi vận hành.', '']
    (ROOT/'BOM.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'BOM: {len(PARTS)} rows, {sum(p[1] for p in PARTS)} parts')

if __name__=='__main__': main()
