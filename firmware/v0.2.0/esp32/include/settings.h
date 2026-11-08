#pragma once
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif
#ifndef DEMO_MODE
#define DEMO_MODE 0
#endif
static const uint32_t SEND_INTERVAL_MS=10000;
static const uint32_t STALE_MS=6000;
static const uint32_t WIFI_RETRY_MS=15000;
static const int AT89S52_RX_PIN=3, AT89S52_TX_PIN=4;
static const int LEVEL_OE_PIN=0;
