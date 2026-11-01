# Firmware and dashboard implementation plan

**Goal:** deliver AT89S52 sensing/display firmware, ESP32 Internet bridge, an importable ThingsBoard dashboard, complete assembly BOM and wiring documentation.

**Time source:** ESP32 obtains NTP and maintains time while powered. AT89S52 mirrors UTC updates received over UART and invalidates them when stale. No external RTC or backup battery.

**Architecture:** AT89S52 at 11,0592 MHz/5 V owns DHT11, OLED and a page button. ESP32-C3 SuperMini exchanges checksummed UART frames with AT89S52 and posts timestamped telemetry over verified HTTPS to the ThingsBoard-compatible device API. Dashboard runs inside the existing IoT platform.

**Stack:** AT89S52 firmware compiled with SDCC mcs51 small model; user programs/verifies HEX with Burn-E; no XC8. PlatformIO Arduino ESP32, portable C protocol/calendar, Python host verification. No cloud credentials are included.

## Steps
- [x] Define and test the portable UART protocol and UTC calendar using native C assertions, including invalid checksum, field overflow and invalid sensor/time flags.
- [x] Implement AT89S52 drivers with bounded waits, no framebuffer, UTC display updates from ESP32 and OLED pages; provide Burn-E HEX programming/verify instructions. Compiled HEX and memory report supplied; no chip verification yet.
- [x] Implement ESP32 UART task and latest-only HTTPS sender; validate certificates, NTP and connection status; discard historical offline records.
- [x] Generate dashboard JSON from the platform's official widget schema, with telemetry cards, history chart/table, server threshold controls and alarms. Add setup instructions for device profile alarm rules.
- [x] Document every signal, physical pin, supply, divider, pull-up, decoupler, oscillator and programming header; deliver CSV and readable BOM plus a standalone SVG wiring diagram.
- [x] Run native protocol tests, ESP32 release/demo builds, dashboard and BOM integrity checks. Report hardware/AT89S52/cloud verification limits explicitly.

## Verification limits
Burn-E Programmer 9.00.88 has AT89S52 in its device list and its pinout was read locally. User will perform hardware Verify themselves. Firmware fits linker limits; hardware DHT/OLED timing and worst-case stack remain bench checks. Local ThingsBoard dashboard already works with synthetic telemetry; physical-device Internet HTTPS deployment remains to be tested.
