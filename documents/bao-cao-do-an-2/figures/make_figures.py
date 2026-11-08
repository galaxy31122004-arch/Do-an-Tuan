"""Build report figures: schematic PNG, block diagram, two flowcharts."""
import pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pymupdf

D = pathlib.Path(__file__).parent
plt.rcParams['font.family'] = 'Times New Roman'

doc = pymupdf.open(D / 'so-do-nguyen-ly.pdf')
doc[0].get_pixmap(dpi=220).save(D / 'so-do-nguyen-ly.png')


def box(ax, x, y, w, h, text, shape='round', fc='white'):
    if shape == 'diamond':
        ax.add_patch(plt.Polygon([(x, y + h / 2), (x + w / 2, y + h), (x + w, y + h / 2), (x + w / 2, y)], fc=fc, ec='black', lw=1.2))
    else:
        style = 'round,pad=0.02,rounding_size=0.25' if shape == 'round' else 'square,pad=0.02'
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec='black', lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=11)


def arrow(ax, a, b, text=None, two=False):
    ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle='<|-|>' if two else '-|>', lw=1.2, color='black'))
    if text:
        ax.text((a[0] + b[0]) / 2 + (0.15 if a[0] == b[0] else 0), (a[1] + b[1]) / 2 + (0 if a[0] == b[0] else 0.15), text, fontsize=9, ha='left' if a[0] == b[0] else 'center')


# --- block diagram ---
fig, ax = plt.subplots(figsize=(11, 6.2)); ax.set_xlim(0, 22); ax.set_ylim(0, 12.4); ax.axis('off')
G = '#eeeeee'
box(ax, 0.3, 10, 4, 1.6, 'Adapter 12 V\nJ1 / J7', 'square', G)
box(ax, 5.5, 10, 4, 1.6, 'D2 SR360\nchống ngược cực', 'square', G)
box(ax, 11, 10, 4, 1.6, 'LM7805\n+5V', 'square', G)
box(ax, 16.5, 10, 5, 1.6, 'ESP32 ổn áp 3,3 V\n+3V3', 'square', G)
arrow(ax, (4.3, 10.8), (5.5, 10.8)); arrow(ax, (9.5, 10.8), (11, 10.8), '+12V'); arrow(ax, (15, 10.8), (16.5, 10.8))
box(ax, 0.3, 5.6, 3.6, 1.6, 'DHT11')
box(ax, 0.3, 3.0, 3.6, 1.6, 'Nút SW1\nđổi trang')
box(ax, 6, 4.2, 4.4, 3.2, 'AT89S52\n(đo, hiển thị,\nđiều khiển relay)', 'square')
box(ax, 12.4, 4.2, 3.8, 3.2, 'TXS0108E\nchuyển mức\n5 V ↔ 3,3 V', 'square')
box(ax, 17.6, 6.0, 4, 1.6, 'OLED SSD1315')
box(ax, 17.6, 3.4, 4, 1.8, 'ESP32-C3\nSuperMini')
box(ax, 17.6, 0.3, 4, 1.6, 'ThingsBoard\nDashboard web', 'round', G)
box(ax, 6, 0.3, 4.4, 1.8, 'PC817 + Q1\nRelay K1 → J6 tải', 'square')
arrow(ax, (3.9, 6.4), (6, 6.4), '1 dây'); arrow(ax, (3.9, 3.8), (6, 4.8))
arrow(ax, (10.4, 6.6), (12.4, 6.6), 'I²C 5 V', True); arrow(ax, (10.4, 5.0), (12.4, 5.0), 'UART 5 V', True)
arrow(ax, (16.2, 6.8), (17.6, 6.8), 'I²C 3,3 V', True); arrow(ax, (16.2, 5.0), (17.6, 4.3), 'UART', True)
arrow(ax, (19.6, 3.4), (19.6, 1.9), 'Wi-Fi / HTTPS', True)
arrow(ax, (8.2, 4.2), (8.2, 2.1), 'P2.0')
arrow(ax, (17.6, 3.8), (14.3, 4.2)); ax.text(15.2, 3.4, 'OE (GPIO0)', fontsize=9)
fig.savefig(D / 'so-do-khoi.png', dpi=200, bbox_inches='tight'); plt.close(fig)


def flow(name, steps, h=1.0):
    n = len(steps)
    fig, ax = plt.subplots(figsize=(6.5, 0.95 * n + 0.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 1.5 * n); ax.axis('off')
    y = 1.5 * n - 1.25
    for i, (kind, text) in enumerate(steps):
        w = 6.4 if kind != 'diamond' else 7
        box(ax, 5 - w / 2, y, w, h, text, kind)
        if i < n - 1:
            arrow(ax, (5, y), (5, y - 0.5))
        y -= 1.5
    fig.savefig(D / name, dpi=200, bbox_inches='tight'); plt.close(fig)


flow('luu-do-at89s52.png', [
    ('round', 'Bắt đầu'),
    ('square', 'P1, P2, P3 = mức cao (relay tắt)\nCấu hình UART 9600, Timer0, ngắt; khởi tạo OLED'),
    ('square', 'Xử lý khung S/T đã nhận; cập nhật đồng hồ'),
    ('square', 'Đọc nút SW1, chống dội 50 ms → đổi trang'),
    ('diamond', 'Đủ chu kỳ 2 s (tick = 0)?'),
    ('square', 'Đọc DHT11 → cập nhật relay (≥ 32 °C bật, ≤ 30 °C tắt,\nlỗi cảm biến: tắt) → gửi khung M'),
    ('square', 'Vẽ lại OLED nếu có thay đổi; trễ 10 ms; quay lại'),
])
flow('luu-do-esp32.png', [
    ('round', 'Bắt đầu'),
    ('square', 'OE = thấp; UART1 9600 (RX GPIO3, TX GPIO4)'),
    ('square', 'Chờ 100 ms → OE = cao; Wi-Fi STA; cấu hình NTP'),
    ('square', 'Tác vụ host-uart: nhận khung M (kiểm CRC) → hàng đợi;\ngửi khung S mỗi 1 s và khung T'),
    ('diamond', 'Wi-Fi + giờ hợp lệ + đủ 10 s?'),
    ('square', 'Lấy bản ghi mới (≤ 6 s) → HTTPS POST telemetry'),
    ('square', 'Cập nhật trạng thái cloud; mất Wi-Fi: thử lại sau 15 s'),
])
print('figures ok')
