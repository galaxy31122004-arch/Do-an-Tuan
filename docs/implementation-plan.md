# Firmware and dashboard implementation plan

**Goal:** deliver PIC sensing/display firmware, ESP32 Internet bridge, an importable ThingsBoard dashboard, complete assembly BOM and wiring documentation.

**Time source:** ESP32 obtains NTP and maintains time while powered. PIC mirrors UTC updates received over UART and invalidates them when stale. No external RTC or backup battery.

**Architecture:** PIC16F877A at 20 MHz/5 V owns DHT11, OLED and a page button. ESP32 DevKit exchanges checksummed UART frames with PIC and posts timestamped telemetry over verified HTTPS to the ThingsBoard-compatible device API. Dashboard runs inside the existing IoT platform.

**Stack:** PIC C source retained; user skips local compiler installation/build and programs HEX with Burn-E. PlatformIO Arduino ESP32, portable C protocol/calendar, Python host verification. No cloud credentials are included.

## Steps
- [x] Define and test the portable UART protocol and UTC calendar using native C assertions, including invalid checksum, field overflow and invalid sensor/time flags.
- [x] Implement PIC drivers with bounded waits, no framebuffer, UTC display updates from ESP32 and OLED pages; provide Burn-E HEX programming/verify instructions. A verified PIC HEX and memory report are not available.
- [x] Implement ESP32 UART task and latest-only HTTPS sender; validate certificates, NTP and connection status; discard historical offline records.
- [x] Generate dashboard JSON from the platform's official widget schema, with telemetry cards, history chart/table, server threshold controls and alarms. Add setup instructions for device profile alarm rules.
- [x] Document every signal, physical pin, supply, divider, pull-up, decoupler, oscillator and programming header; deliver CSV and readable BOM plus a standalone SVG wiring diagram.
- [x] Run native protocol tests, ESP32 release/demo builds, dashboard and BOM integrity checks. Report hardware/PIC/cloud verification limits explicitly.

## Verification limits
User owns a Burn-E programmer; exact revision, cable pinout and software were not provided. Local compiler installation/build is excluded at the user's request. No assembled PCB or cloud account has been provided. Build ESP32 locally; do not upload or create cloud resources. Dashboard import needs confirmation against the actual deployment.
