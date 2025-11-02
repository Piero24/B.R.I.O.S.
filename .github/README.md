<div id="top"></div>
<br/>
<br/>

<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/3145/3145073.png" width="105" height="100">
</p>
<h1 align="center">
    <a href="https://github.com/Piero24/Bleissant">Bleissant</a>
</h1>
<p align="center">
    <!-- BADGE -->
    <!--
        *** You can make other badges here
        *** [shields.io](https://shields.io/)
        *** or here
        *** [CircleCI](https://circleci.com/)
    -->
    <a href="https://github.com/Piero24/Bleissant/commits/main">
    <img src="https://img.shields.io/github/last-commit/piero24/Bleissant">
    </a>
    <a href="https://github.com/Piero24/Bleissant">
    <img src="https://img.shields.io/badge/Maintained-yes-green.svg">
    </a>
    <!--<a href="https://github.com/Piero24/Bleissant">
    <img src="https://img.shields.io/badge/Maintained%3F-no-red.svg">
    </a> -->
    <a href="https://github.com/Piero24/Bleissant/issues">
    <img src="https://img.shields.io/github/issues/piero24/Bleissant">
    </a>
    <a href="https://github.com/Piero24/Bleissant/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/piero24/Bleissant">
    </a>
</p>
<p align="center">
    A professional BLE proximity monitor that automatically locks your Mac when your device moves out of range
    <br/>
    <br/>
    <a href="#prerequisites">Requirements</a>
    •
    <a href="https://github.com/Piero24/Bleissant/issues">Report Bug</a>
    •
    <a href="https://github.com/Piero24/Bleissant/issues">Request Feature</a>
</p>


---


<br/><br/>
<h2 id="introduction">📔  Introduction</h2>
<p>
    This project is a professional-grade BLE (Bluetooth Low Energy) proximity monitoring tool designed specifically for macOS. It <strong>continuously tracks the distance to a designated BLE device</strong> (such as your iPhone, Apple Watch, or any BLE beacon) using signal strength analysis and automatically locks your Mac when the device moves beyond a configurable threshold.
</p>
<br/>
<p>
    The aim of this project is to enhance your Mac's security by leveraging the proximity of your personal device as a security token. When you walk away with your phone, your Mac automatically locks—providing an extra layer of protection without any manual intervention. This seamless integration ensures your workspace remains secure while maintaining a smooth, uninterrupted workflow.
</p>
<br/>
<div align="center">
    <img src="https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=800&auto=format&fit=crop" style="width: 100%;" width="100%">
    <p>Image: Bluetooth proximity monitoring for enhanced security</p>
</div>
<br/>
<p>
    Bleissant employs a sophisticated distance estimation algorithm based on the <strong>Log-Distance Path Loss Model</strong>, which calculates the distance between your Mac and the target BLE device using RSSI (Received Signal Strength Indicator). The application maintains a rolling buffer of recent RSSI samples (configurable, default: 12 readings), applies statistical smoothing to filter out momentary fluctuations, and uses the smoothed values to calculate accurate distance measurements.
</p>

> [!NOTE]
> The distance estimation is calculated using the formula: **d = 10^((TX_power - RSSI) / (10 * n))**, where TX_power is the calibrated signal strength at 1 meter, RSSI is the smoothed signal reading, and n is the path loss exponent (environment-dependent).

<div align="center">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Signal_strength_vs_distance.svg/800px-Signal_strength_vs_distance.svg.png" style="width: 100%;" width="100%">
    <p>Image: Signal strength decreases logarithmically with distance</p>
</div>

<br/>  
<p>
    <strong>DISCOVERY</strong>: The program includes a discovery scanner that finds all nearby BLE devices. You can run the scanner for a specified duration (5-60 seconds) to discover device addresses, names, signal strengths, and estimated distances. This is particularly useful for finding the MAC address or UUID of your target device before setting up monitoring.
</p>
<p>
    <strong>MONITORING</strong>: The monitoring phase continuously scans for BLE advertisements from your target device and processes the signal strength following these steps:
    <ol>
        <li>
            <strong>Signal Collection</strong>
            <p>
                The application receives BLE advertisements from the target device and extracts the RSSI values. Each advertisement provides real-time signal strength data.
            </p>
        </li>
        <li>
            <strong>Signal Smoothing</strong>
            <p>
                RSSI values are added to a rolling buffer (deque) and the statistical mean is calculated. This smoothing process eliminates temporary signal fluctuations and provides stable distance measurements.
            </p>
        </li>
        <li>
            <strong>Distance Calculation</strong>
            <p>
                Using the Log-Distance Path Loss model, the application calculates the distance between your Mac and the device. This calculation takes into account the calibrated TX power and environmental path loss exponent.
            </p>
        </li>
        <li>
            <strong>Proximity Alert & Lock</strong>
            <p>
                When the calculated distance exceeds the configured threshold (default: 2.0 meters), the application triggers a macOS lock command. Your Mac is immediately locked and requires a password to unlock. When the device returns to range, you receive a notification.
            </p>
        </li>
    </ol>
</p>
<br/>
<div align="center">
    <img src="https://cdn-icons-png.flaticon.com/512/3064/3064197.png" style="width: 50%;" width="50%">
    <p>Image: Automatic Mac locking based on device proximity</p>
</div>
<br/>
<br/>
<p>
    <strong>SERVICE MODE</strong>: Bleissant can run as a background daemon, allowing continuous monitoring without keeping a terminal window open. The service manager provides commands to start, stop, restart, and check the status of the background monitor. All activity can be logged to a file for later review.
</p>

<p align="right"><a href="#top">⇧</a></p>

<h2 id="made-in"><br/>🛠  Built With</h2>
<p>
    This project is entirely written in Python and uses the Bleak library for cross-platform Bluetooth Low Energy communication, python-dotenv for configuration management, and PyObjC frameworks for native macOS integration.
</p>
<p align="center">
    <a href="https://www.python.org/">Python 3.8+</a> • <a href="https://github.com/hbldh/bleak">Bleak</a> • <a href="https://github.com/theskumar/python-dotenv">python-dotenv</a> • <a href="https://pyobjc.readthedocs.io/">PyObjC</a>
</p>
<p align="right"><a href="#top">⇧</a></p>

<h2 id="documentation"><br/><br/>📚  Documentation</h2>

> [!TIP]
> Use the `--scanner` mode to discover nearby BLE devices and find your target device's MAC address or UUID. Always use the `-m` flag on macOS for more reliable device tracking with real MAC addresses instead of randomized UUIDs.

<p>
    Bleissant is highly customizable. You can configure the <strong>target device address</strong>, <strong>distance threshold</strong>, <strong>TX power calibration</strong>, <strong>path loss exponent</strong>, and <strong>sample window size</strong> through the `.env` configuration file. The application supports three main operating modes: <strong>Discovery Scanner</strong> (find devices), <strong>Monitor Mode</strong> (foreground monitoring with real-time output), and <strong>Background Service</strong> (daemon mode with service management).
</p>
<p>
    Additionally, you have full control over output verbosity and logging options. Enable <strong>verbose mode</strong> with `-v` to see detailed RSSI values, smoothed signals, estimated distances, and signal strength indicators in real-time. Enable <strong>file logging</strong> with `-f` to write all activity to a log file, which is particularly useful when running as a background service.
</p>
<p>
    The distance estimation algorithm can be fine-tuned for your specific environment by adjusting the path loss exponent. Indoor environments with walls and obstacles typically require values between 2.5-4.0, while open spaces can use values closer to 2.0.
</p>

> [!NOTE]
> For best accuracy, calibrate the `TX_POWER_AT_1M` value by placing your device exactly 1 meter from your Mac, running the monitor in verbose mode, and noting the average RSSI value.

<p>
    All command-line arguments and configuration options are documented below in the <a href="#how-to-start">How to Start</a> section.
</p>

> [!WARNING]  
> The **background service mode** (`--start`) will keep the monitor running even after you close the terminal. Always use `--stop` to properly terminate the background process before making configuration changes.


<p align="right"><a href="#top">⇧</a></p>


<h2 id="prerequisites"><br/>🧰  Prerequisites</h2>
<p>
    The only prerequisites for running this project are Python 3.8 or higher and the required Python packages. All dependencies are listed in the `requirements.txt` file and can be installed with pip.
</p>

**System Requirements:**

- macOS 10.15 (Catalina) or later
- Python 3.8+
- Bluetooth Low Energy adapter (built-in on all modern Macs)

**Python Dependencies:**

- `bleak` - Cross-platform BLE library
- `python-dotenv` - Configuration file management
- `pyobjc-framework-CoreBluetooth` - macOS Bluetooth support
- `pyobjc-framework-Cocoa` - macOS system integration

<br/>

Install all dependencies with:

```sh
pip install -r requirements.txt
```

<p align="right"><a href="#top">⇧</a></p>


<h2 id="how-to-start"><br/>⚙️  How to Start</h2>
<p>
    Depending on whether you want to discover devices, monitor in the foreground, or run as a background service, you have different parameters available. The following guide covers all operating modes.
</p>
<br/>

1. Clone the repo
  
```sh
git clone https://github.com/Piero24/Bleissant.git
cd Bleissant
```

2. Create and activate a virtual environment

```sh
python3 -m venv env
source env/bin/activate
```

3. Install dependencies
  
```sh
pip install -r requirements.txt
```

4. Configure your target device

    4.1 First, discover nearby BLE devices to find your target device's address:
  
    ```sh
    python3 main.py --scanner 15 -m
    ```
    
    This will scan for 15 seconds and display all discovered devices with their MAC addresses, names, RSSI values, and estimated distances.

    4.2 Copy the example configuration file and edit it:
  
    ```sh
    cp .env.example .env
    nano .env  # or use your preferred editor
    ```
    
    4.3 Update the `.env` file with your device information:
    
    ```bash
    TARGET_DEVICE_MAC_ADDRESS=XX:XX:XX:XX:XX:XX  # Your device's MAC
    TARGET_DEVICE_NAME=My iPhone                  # Device name
    TARGET_DEVICE_TYPE=iPhone 15 Pro             # Device type
    DISTANCE_THRESHOLD_M=2.0                     # Lock distance
    ```

5. Now depending on your desired operating mode, use the appropriate command:

    5.1 **Discovery Mode** - Scan for nearby BLE devices:
  
    ```sh
    # Scan for 15 seconds using MAC addresses (recommended for macOS)
    python3 main.py --scanner 15 -m
    
    # Scan for 30 seconds using UUIDs
    python3 main.py --scanner 30
    ```

    5.2 **Monitor Mode (Foreground)** - Real-time monitoring with terminal output:
  
    ```sh
    # Monitor using default MAC from .env with verbose output
    python3 main.py --target-mac -v
    
    # Monitor specific device with file logging
    python3 main.py --target-mac "A1:B2:C3:D4:E5:F6" -m -v -f
    
    # Monitor using UUID (macOS privacy mode)
    python3 main.py --target-uuid -v
    ```

    5.3 **Background Service Mode** - Run as a daemon:
  
    ```sh
    # Start the background monitor
    python3 main.py --target-mac -v -f --start
    
    # Check service status
    python3 main.py --status
    
    # Stop the service
    python3 main.py --stop
    
    # Restart the service
    python3 main.py --restart
    ```

> [!NOTE] 
> 1. When running in background mode with file logging (`-f`), all output is written to `.ble_monitor.log` in the project directory.
> 2. The PID of the background process is stored in `.ble_monitor.pid`.
> 3. Always use `-m` flag on macOS for better device tracking reliability.

<br/>

**Command-Line Arguments:**

| Argument | Short | Description |
|----------|-------|-------------|
| `--scanner SECONDS` | `-s` | Discover BLE devices for specified duration (5-60s) |
| `--target-mac [ADDRESS]` | `-tm` | Monitor by MAC address (use default from .env if no address provided) |
| `--target-uuid [UUID]` | `-tu` | Monitor by UUID (macOS privacy mode) |
| `--macos-use-bdaddr` | `-m` | Force MAC address mode on macOS (recommended) |
| `--verbose` | `-v` | Enable detailed RSSI and distance output |
| `--file-logging` | `-f` | Enable logging to file |
| `--start` | | Start as background daemon |
| `--stop` | | Stop background daemon |
| `--restart` | | Restart background daemon |
| `--status` | | Show daemon status and recent activity |

<br/>

**Example Output (Monitor Mode):**

```
Starting BLE Monitor
──────────────────────────────────────────────────
Target:     Pietro's iPhone (iPhone 15 Pro)
Address:    A1:B2:C3:D4:E5:F6
Threshold:  2.0m
TX Power:   -59 dBm @ 1m
Path Loss:  2.8
Samples:    12 readings
Mode:       BD_ADDR (MAC)
──────────────────────────────────────────────────

● Monitoring active - Press Ctrl+C to stop

[14:32:15] RSSI:  -52 dBm → Smoothed:  -51.3 dBm │ Distance:  0.56m │ Signal: Strong
[14:32:16] RSSI:  -54 dBm → Smoothed:  -52.1 dBm │ Distance:  0.61m │ Signal: Strong
[14:32:17] RSSI:  -75 dBm → Smoothed:  -69.1 dBm │ Distance:  2.81m │ Signal: Weak

──────────────────────────────────────────────────
⚠  ALERT: Device moved out of range
   Device:    Pietro's iPhone
   Distance:  ~2.81m (threshold: 2.0m)
   Time:      14:32:17
   Action:    🔒 MacBook locked (password required)
──────────────────────────────────────────────────
```

<br/>
<p align="right"><a href="#top">⇧</a></p>


---


<h3 id="responsible-disclosure"><br/>📮  Responsible Disclosure</h3>
<p>
    We assume no responsibility for an improper use of this code and everything related to it. We do not assume any responsibility for damage caused to people and / or objects in the use of the code.
</p>
<strong>
    By using this code even in a small part, the developers are declined from any responsibility.
</strong>
<br/>
<br/>
<p>
    It is possible to have more information by viewing the following links: 
    <a href="#code-of-conduct"><strong>Code of conduct</strong></a>
     • 
    <a href="#license"><strong>License</strong></a>
</p>

<p align="right"><a href="#top">⇧</a></p>


<h3 id="report-a-bug"><br/>🐛  Bug and Feature</h3>
<p>
    To <strong>report a bug</strong> or to request the implementation of <strong>new features</strong>, it is strongly recommended to use the <a href="https://github.com/Piero24/Bleissant/issues"><strong>ISSUES tool from Github »</strong></a>
</p>
<br/>
<p>
    Here you may already find the answer to the problem you have encountered, in case it has already happened to other people. Otherwise you can report the bugs found.
</p>
<br/>
<strong>
    ATTENTION: To speed up the resolution of problems, it is recommended to answer all the questions present in the request phase in an exhaustive manner.
</strong>
<br/>
<br/>
<p>
    (Even in the phase of requests for the implementation of new functions, we ask you to better specify the reasons for the request and what final result you want to obtain).
</p>
<br/>

<p align="right"><a href="#top">⇧</a></p>
  
 --- 

<h2 id="license"><br/>🔍  License</h2>
<strong>MIT LICENSE</strong>
<br/>
<br/>
<i>Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including...</i>
<br/>
<br/>
<a href="https://github.com/Piero24/Bleissant/blob/main/LICENSE">
    <strong>License Documentation »</strong>
</a>
<br/>
<p align="right"><a href="#top">⇧</a></p>


<h3 id="third-party-licenses"><br/>📌  Third Party Licenses</h3>

In the event that the software uses third-party components for its operation, 
<br/>
the individual licenses are indicated in the following section.
<br/>
<br/>
<strong>Software list:</strong>
<br/>
<table>
  <tr  align="center">
    <th>Software</th>
    <th>License owner</th> 
    <th>License type</th> 
    <th>Link</th>
  </tr>
  <tr  align="center">
    <td>Bleak</td>
    <td><a href="https://github.com/hbldh/bleak">hbldh</a></td>
    <td>MIT</td>
    <td><a href="https://github.com/hbldh/bleak">here</a></td>
  </tr>
  <tr  align="center">
    <td>python-dotenv</td> 
    <td><a href="https://github.com/theskumar">theskumar</a></td>
    <td>BSD-3-Clause</td>
    <td><a href="https://github.com/theskumar/python-dotenv">here</a></td>
  </tr>
  <tr  align="center">
    <td>PyObjC</td>
    <td><a href="https://github.com/ronaldoussoren/pyobjc">PyObjC Team</a></td>
    <td>MIT</td>
    <td><a href="https://github.com/ronaldoussoren/pyobjc">here</a></td>
  </tr>
</table>

<p align="right"><a href="#top">⇧</a></p>


---
> *<p align="center"> Copyright (C) by Pietrobon Andrea <br/> Released date: 02-11-2024*
