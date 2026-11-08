#pragma once
/* Copy to secrets.h. Never commit Wi-Fi passwords or device credentials. */
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
/* Origin only, no trailing slash. The device HTTP API must be enabled. */
#define IOT_ORIGIN "https://YOUR_THINGSBOARD_HOST"
#define IOT_TOKEN "YOUR_DEVICE_ACCESS_TOKEN"
/* PEM root CA of your deployment. TLS verification is mandatory. */
static const char IOT_ROOT_CA[] = R"PEM(-----BEGIN CERTIFICATE-----
REPLACE_WITH_YOUR_DEPLOYMENT_ROOT_CA
-----END CERTIFICATE-----
)PEM";
