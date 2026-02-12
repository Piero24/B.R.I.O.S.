import os
from dotenv import load_dotenv

# --- Configuration Loader ---
# Load user-defined settings from multiple possible locations:
# 1. Current working directory (.env)
# 2. User home directory (~/.brios.env)
# 3. Dedicated config directory (~/.config/brios/config)
load_dotenv(".env")
load_dotenv(os.path.expanduser("~/.brios.env"))
load_dotenv(os.path.expanduser("~/.config/brios/config"))

# --- Application Constants ---
# The target device's address. This can be a MAC address (on most platforms)
# or a UUID-based address (common on macOS due to privacy features).
TARGET_DEVICE_MAC_ADDRESS = os.getenv("TARGET_DEVICE_MAC_ADDRESS")
TARGET_DEVICE_UUID_ADDRESS = os.getenv("TARGET_DEVICE_UUID_ADDRESS")

# A human-readable name for the target device, used in logs and alerts.
TARGET_DEVICE_NAME = os.getenv("TARGET_DEVICE_NAME", "Unknown Device Name")
TARGET_DEVICE_TYPE = os.getenv("TARGET_DEVICE_TYPE", "Unknown Device")

# RSSI value (in dBm) of the target device measured at a distance of 1 meter.
# This value is crucial for accurate distance estimation.
TX_POWER_AT_1M = int(os.getenv("TX_POWER_AT_1M", "-59"))

# The path-loss exponent (n) for the environment. This value describes the rate
# at which the signal strength decreases with distance. Common values range
# from 2.0 (free space) to 4.0 (obstructed environments).
PATH_LOSS_EXPONENT = float(os.getenv("PATH_LOSS_EXPONENT", "2.8"))

# The number of recent RSSI samples to average for smoothing out fluctuations.
SAMPLE_WINDOW = int(os.getenv("SAMPLE_WINDOW", "12"))

# The distance (in meters) beyond which a device is considered "out of range."
DISTANCE_THRESHOLD_M = float(os.getenv("DISTANCE_THRESHOLD_M", "2.0"))

# --- Reliability & Safety Constants ---
# Time (in seconds) to ignore "out of range" signals after unlocking/resuming.
# Prevents immediate re-locking while signal stabilizes.
GRACE_PERIOD_SECONDS = int(os.getenv("GRACE_PERIOD_SECONDS", "30"))

# Lock Loop Protection:
# If the Mac locks LOCK_LOOP_THRESHOLD times within LOCK_LOOP_WINDOW seconds,
# the script will pause for LOCK_LOOP_PENALTY seconds.
LOCK_LOOP_THRESHOLD = int(os.getenv("LOCK_LOOP_THRESHOLD", "3"))
LOCK_LOOP_WINDOW = int(os.getenv("LOCK_LOOP_WINDOW", "60"))
LOCK_LOOP_PENALTY = int(os.getenv("LOCK_LOOP_PENALTY", "120"))
