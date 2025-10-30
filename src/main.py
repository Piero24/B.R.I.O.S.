# https://github.com/hbldh/bleak
# pip install bleak

import asyncio

import structlog
from parser import parser_generator
from log.logging import setup_logging
from src.scanner import start_scanner


setup_logging()
log = structlog.get_logger()

if __name__ == "__main__":
    parser = parser_generator()
    args = parser.parse_args()

    try:
        asyncio.run(start_scanner(args))
    except KeyboardInterrupt:
        log.info("\nProgram interrupted by user (Ctrl+C).")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")