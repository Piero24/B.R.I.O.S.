#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🥐 B.R.I.O.S. - Bluetooth Reactive Intelligent Operator for Croissant Safety

A professional proximity monitoring tool for device tracking and automated security.

This script provides a command-line interface to scan for Bluetooth devices
and monitor a specific target device's proximity based on its
Received Signal Strength Indicator (RSSI). It can be run as a foreground
process for immediate monitoring or as a background daemon for continuous
operation.

Key features include:
  - Real-time RSSI signal strength monitoring.
  - Distance estimation using the Log-Distance Path Loss model.
  - Proximity alerts when a device moves beyond a configurable threshold.
  - A discovery scanner to find nearby devices.
  - Service management for starting, stopping, and checking the monitor's
    status as a background process.
"""
from .cli import main

if __name__ == "__main__":
    main()
