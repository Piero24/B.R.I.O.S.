import argparse

import structlog


log = structlog.get_logger()

def parser_generator() -> argparse.ArgumentParser:
    """
    """
    parser = argparse.ArgumentParser(
        description="Continuously monitor the distance of a specific BLE device."
    )

    log.info("Text Message")

    # TODO: Add parse scanner

    parser.add_argument(
        "--services",
        "-s",
        metavar="<uuid>",
        nargs="*",
        help="UUIDs of one or more services to filter for.",
    )
    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="Use Bluetooth address instead of UUID on macOS. Recommended.",
    )
    parser.add_argument(
        "--scan-duration",
        "-sd",
        type=int,
        default=5,
        metavar="<seconds>",
        help="Duration of each BLE scan in seconds (default: 5).",
    )
    parser.add_argument(
        "--uuid",
        "-u",
        action="store_true",
        help="Use UUIDs instead of MAC addresses to identify target devices.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output for debugging purposes.",
    )
    return parser