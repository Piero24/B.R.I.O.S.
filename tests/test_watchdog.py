import asyncio
import sys
import unittest
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

class TestWatchdog(unittest.IsolatedAsyncioTestCase):
    async def test_watchdog_triggers_handler(self):
        """Test that watchdog triggers _handle_screen_lock when screen is locked."""
        print("\nTesting watchdog...")
        
        test_mac = os.getenv('TEST_DEVICE_MAC', "00:00:00:00:00:00")
        flags = Flags(daemon_mode=False, file_logging=False, verbose=True)
        monitor = DeviceMonitor(test_mac, True, flags)
        monitor.scanner = AsyncMock()
        
        # Mock _handle_screen_lock to set a flag when called
        handler_called = asyncio.Event()
        
        async def mock_handler():
            print("Handler triggered!")
            monitor.is_handling_lock = True
            handler_called.set()
            await asyncio.sleep(0.1)
            monitor.is_handling_lock = False
            
        monitor._handle_screen_lock = mock_handler
        
        # Mock _is_screen_locked to return True
        monitor._is_screen_locked = MagicMock(return_value=True)
        
        # Start watchdog
        watchdog_task = asyncio.create_task(monitor._watchdog_loop())
        
        # Wait for handler to be called
        try:
            await asyncio.wait_for(handler_called.wait(), timeout=2.0)
            print("✓ Watchdog successfully triggered handler.")
        except asyncio.TimeoutError:
            self.fail("Watchdog failed to trigger handler within timeout.")
        finally:
            watchdog_task.cancel()

if __name__ == '__main__':
    unittest.main()
