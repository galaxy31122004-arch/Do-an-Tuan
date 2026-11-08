"""Layout v2: ESP32-C3 and TXS0108E as single module symbols, relay driver on board."""
# ref: (x_g, y_g, rotation, mirror)  mirror: None | 'x' | 'y'   (grid = 2.54 mm)
PLACE = {
    # 3V3 side, far left
    'J4': (18, 24, 0, 'y'), 'U2': (14, 40, 0, None), 'R4': (24, 52, 0, None),
    'C5': (24, 20.5, 0, None), 'C8': (27, 20.5, 0, None),          # OLED 3V3
    'C6': (9, 30.5, 0, None), 'C7': (6, 30.5, 0, None),            # ESP32 5V
    # level shifter between the two domains
    'U4': (54, 34, 0, None),
    'C13': (47.5, 27, 270, None), 'C3': (60.5, 27, 90, None),      # TXS VA / VB
    # AT89S52 column
    'J3': (54, 22, 0, 'y'), 'U5': (54, 44, 0, None), 'C12': (50, 42.5, 0, None),
    'R2': (54, 52, 0, None), 'Y1': (54, 60, 90, None), 'C9': (54, 67, 0, None),
    'C10': (54, 74, 0, None), 'C2': (54, 81, 0, None), 'R1': (54, 88, 0, None),
    'SW2': (54, 94, 0, None), 'R3': (54, 100, 0, None), 'SW1': (54, 107, 0, 'y'),
    'U1': (102, 60, 0, None), 'C1': (112, 45.5, 0, None), 'C11': (116, 45.5, 0, None),
    # relay driver: P2.0 low -> PC817 LED on -> 2SC1815 on -> coil energised (active-low, no power-up pulse)
    'R6': (109, 56.5, 0, None), 'U8': (114, 60, 0, None), 'R5': (119.5, 61, 90, None),
    'R7': (122, 64.5, 0, None), 'Q1Y': (125, 61, 0, None), 'D3': (123, 53, 270, None),
    'K1': (128, 53, 0, None), 'J6Y': (137, 52, 0, None),
    # power entry
    'J1X': (4, 10, 0, None), 'J7': (4, 15, 0, 'y'), 'D2X': (11, 9, 0, 'y'), 'C14': (15, 12.5, 0, None),
    'C15': (17, 12.5, 0, None), 'U7': (21, 9, 0, None), 'C16': (26, 12.5, 0, None),
    'R10': (30, 11.5, 0, None), 'D1': (34, 15, 0, 'y'),
    'TP1': (78, 10, 0, None), 'TP2': (82, 10, 0, None), 'TP3': (86, 10, 0, None),
    '#FLG01': (13, 7, 0, None), '#FLG02': (96, 10, 0, None),
}
NEW_PARTS = {  # ref: (project symbol, value)
    'U2': ('ESP32-C3_SuperMini', 'ESP32-C3 SuperMini'),
    'U4': ('TXS0108E_Module', 'TXS0108E module'),
}
NETS = {
    '+5V': 'U1.40 U1.31 U7.3 C16.1 R10.1 C6.1 C7.1 TP1.1 C1.1 C11.1 C2.1 SW2.1 R3.1 U5.1 R2.1 C12.1 J3.2 '
           'U4.11 C3.1 U2.1 R6.1',
    'GND': 'U1.20 J1X.2 J7.2 U7.2 C14.2 C15.2 C16.2 D1.1 C6.2 C7.2 TP3.1 #FLG02.1 C1.2 C11.2 C9.2 C10.2 R1.2 SW1.2 '
           'U5.4 C12.2 J3.3 U4.20 C13.2 C3.2 R4.2 U2.2 J4.1 C5.2 C8.2 Q1Y.1 R7.2',
    '+3V3': 'TP2.1 U4.1 C13.1 U2.3 J4.2 C5.1 C8.1',
    # +12V = after SR360, before LM7805; the relay side (opto collector, coil, D3) runs from it
    'VJACK': 'J1X.1 J7.1 D2X.2', '+12V': 'D2X.1 C14.1 C15.1 U7.1 #FLG01.1 U8.4 K1.5 D3.1', 'LED_A': 'R10.2 D1.2',
    'RST': 'U1.9 C2.2 R1.1 SW2.2 J3.1', 'XTAL1': 'U1.19 Y1.1 C9.1', 'XTAL2': 'U1.18 Y1.2 C10.1',
    'SDA5': 'U1.1 U4.12', 'SCL5': 'U1.2 U4.13', 'MOSI': 'U1.6 J3.6', 'MISO': 'U1.7 J3.4', 'SCK': 'U1.8 J3.5',
    'TX51': 'U1.11 U4.14', 'RX51': 'U1.10 U4.15', 'DHT_DATA': 'U1.12 U5.2 R2.2', 'BTN_PAGE': 'U1.13 R3.2 SW1.1',
    'RELAY_IN': 'U1.21 U8.2', 'LED_RLY': 'R6.2 U8.1', 'OPTO_E': 'U8.3 R5.1', 'QB': 'R5.2 Q1Y.3 R7.1', 'COIL_LO': 'Q1Y.2 K1.2 D3.2',
    'RLY_COM': 'K1.1 J6Y.1', 'RLY_NC': 'K1.4 J6Y.2',
    'SDA3': 'U4.2 J4.4', 'SCL3': 'U4.3 J4.3', 'TX51_3V3': 'U4.4 U2.4', 'RX51_3V3': 'U4.5 U2.9',
    'OE': 'U4.10 U2.10 R4.1',
}
TRUNK = {
    'RST': 94, 'SDA5': 92, 'SCL5': 90, 'MOSI': 88, 'MISO': 86, 'SCK': 84, 'RX51': 82, 'TX51': 80,
    'DHT_DATA': 78, 'BTN_PAGE': 76, 'XTAL2': 74, 'XTAL1': 72,
    'SDA3': 34, 'SCL3': 32, 'TX51_3V3': 30, 'RX51_3V3': 28, 'OE': 26,
}
MANUAL = {
    'VJACK': [[(7, 9), (9.5, 9)], [(6, 15), (8.5, 15), (8.5, 9)]],   # jack and 12V terminal in parallel
    '+12V': [[(12.5, 9), (18, 9)], [(15, 11), (15, 9)], [(17, 11), (17, 9)], [(13, 7), (13, 9)]],
    'LED_A': [[(30, 13), (30, 15), (32.5, 15)]],
    '+5V': [[(102, 44), (116, 44)],                          # U1 VCC -> C1, C11
            [(13, 32), (13, 29), (6, 29)],                   # ESP32 5V -> C6, C7
            [(57, 29), (58, 29), (58, 27), (59, 27)],        # TXS VB -> C3
            [(54, 41), (50, 41)],                            # DHT11 VDD -> C12
            [(24, 9), (26, 9), (26, 11)]],                   # LM7805 OUT -> C16
    '+3V3': [[(51, 29), (50, 29), (50, 27), (49, 27)],       # TXS VA -> C13
             [(20, 24), (22, 24), (22, 19), (27, 19)]],      # OLED VCC -> C5, C8
    'RELAY_IN': [[(108, 61), (111, 61)]],
    'LED_RLY': [[(109, 58), (109, 59), (111, 59)]],
    'OPTO_E': [[(117, 61), (118, 61)]],
    'QB': [[(121, 61), (123, 61)], [(122, 61), (122, 63)]],
    'COIL_LO': [[(126, 56), (126, 59)], [(123, 54.5), (123, 57.5), (126, 57.5)]],
    'RLY_COM': [[(130, 56), (130, 57), (133, 57), (133, 52), (135, 52)]],
    'RLY_NC': [[(129, 50), (129, 47), (132, 47), (132, 53), (135, 53)]],
}
MANUAL['+12V'].append([(123, 51.5), (123, 50), (126, 50)])   # D3 cathode -> coil top (+12V)
MANUAL_JUNCTIONS = [(126, 50), (8.5, 9), (13, 9), (15, 9), (17, 9), (112, 44), (13, 29), (9, 29), (58, 27), (50, 27),
                    (24, 19), (26, 9), (122, 61), (126, 57.5)]
SKIP_POWER = {'D2X.1', 'C14.1', 'C15.1', 'U7.1', '#FLG01.1', 'D3.1', 'U1.40', 'C11.1', 'U2.1', 'C6.1', 'C7.1', 'U4.11', 'C3.1', 'U4.1', 'C13.1', 'U5.1',
              'J4.2', 'C8.1', 'U7.3', 'C16.1', 'D3.1'}
EXTRA_POWER = [('+12V', 17, 9), ('+5V', 13, 29), ('+5V', 58, 27), ('+3V3', 50, 27), ('+5V', 26, 9)]
RENAME = {'J1X': 'J1', 'D2X': 'D2', 'Q1Y': 'Q1', 'J6Y': 'J6'}
TMP_LIB = {'J1X': 'Connector:Barrel_Jack_Switch', 'D2X': 'Device:D', 'Q1Y': 'Transistor_BJT:Q_NPN_ECB',
           'J6Y': 'Connector:Screw_Terminal_01x02'}
VALUES = {'R6': '2k2', 'D2X': 'SR360', 'K1': 'SRD-12VDC-SL-C', 'R5': '4k7'}
FOOTPRINTS = {'D2X': 'Diode_THT:D_DO-201AD_P15.24mm_Horizontal'}
CAPTIONS = {}
NC = ('J1X.3 K1.3 U5.3 U1.3 U1.4 U1.5 U1.14 U1.15 U1.16 U1.17 U1.22 U1.23 U1.24 U1.25 U1.26 U1.27 U1.28 U1.29 U1.30 '
      'U1.32 U1.33 U1.34 U1.35 U1.36 U1.37 U1.38 U1.39 U4.6 U4.7 U4.8 U4.9 U4.16 U4.17 U4.18 U4.19 '
      'U2.5 U2.6 U2.7 U2.8 U2.11 U2.12 U2.13 U2.14 U2.15 U2.16')
