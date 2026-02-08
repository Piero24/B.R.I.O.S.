import asyncio
import sys
import unittest
import time
import os
from unittest.mock import MagicMock, AsyncMock, patch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock dependencies before importing main
sys.modules['dotenv'] = MagicMock()
sys.modules['bleak'] = MagicMock()
sys.modules['bleak.backends.device'] = MagicMock()
sys.modules['bleak.backends.scanner'] = MagicMock()

# Add the project directory to sys.path to import main
project_root = os.getenv('PROJECT_ROOT')
sys.path.append(project_root)

from main import DeviceMonitor, Flags

class TestHeartbeat(unittest.IsolatedAsyncioTestCase):
    async def test_heartbeat_restarts_scanner(self):
        """Test that watchdog restarts scanner if no packets received for timeout."""
        print("\nTesting heartbeat...")
        
        test_mac = os.getenv('TEST_DEVICE_MAC', "00:00:00:00:00:00")
        flags = Flags(daemon_mode=False, file_logging=False, verbose=True)
        monitor = DeviceMonitor(test_mac, True, flags)
        monitor.scanner = AsyncMock()
        
        # Mock _handle_screen_lock to set a flag when called
        handler_called = asyncio.Event()
        
        async def mock_handler():
            print("Handler triggered by heartbeat!")
            monitor.is_handling_lock = True
            handler_called.set()
            await asyncio.sleep(0.1)
            monitor.is_handling_lock = False
            
        monitor._handle_screen_lock = mock_handler
        
        # Mock _is_screen_locked to return False (so we test heartbeat, not lock)
        monitor._is_screen_locked = MagicMock(return_value=False)
        
        # Set last_packet_time to be very old (more than 120s ago)
        monitor.last_packet_time = time.time() - 200
        
        # Start watchdog
        watchdog_task = asyncio.create_task(monitor._watchdog_loop())
        
        # Wait for handler to be called
        try:
            await asyncio.wait_for(handler_called.wait(), timeout=3.0)
            print("✓ Heartbeat successfully triggered restart.")
        except asyncio.TimeoutError:
            self.fail("Heartbeat failed to trigger restart within timeout.")
        finally:
            watchdog_task.cancel()

if __name__ == '__main__':
    unittest.main()
