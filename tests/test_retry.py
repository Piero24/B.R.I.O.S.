import asyncio
import sys
import unittest
import os
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
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

from main import DeviceMonitor, Flags, Colors

class TestDeviceMonitorRetry(unittest.IsolatedAsyncioTestCase):
    async def test_handle_screen_lock_retry_success(self):
        """Test that _handle_screen_lock retries and eventually succeeds."""
        print("\nTesting retry logic: Success after 2 failures...")
        
        # Mock dependencies
        mock_scanner = AsyncMock()
        # Fail twice, then succeed
        mock_scanner.start.side_effect = [
            Exception("Bluetooth busy"),
            Exception("Bluetooth busy"),
            None
        ]
        
        test_mac = os.getenv('TEST_DEVICE_MAC', "00:00:00:00:00:00")
        flags = Flags(daemon_mode=False, file_logging=False, verbose=True)
        monitor = DeviceMonitor(test_mac, True, flags)
        monitor.scanner = mock_scanner
        
        # Mock _is_screen_locked to return True once then False (to exit the waiting loop)
        monitor._is_screen_locked = MagicMock(side_effect=[True, False])
        
        # Mock asyncio.sleep to speed up test
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            await monitor._handle_screen_lock()
            
            # Verify start was called 3 times (2 failures + 1 success)
            self.assertEqual(mock_scanner.start.call_count, 3)
            print("✓ Retry logic worked: 3 attempts made as expected.")

    async def test_handle_screen_lock_retry_failure(self):
        """Test that _handle_screen_lock gives up after max retries."""
        print("\nTesting retry logic: Failure after max retries...")
        
        # Mock dependencies
        mock_scanner = AsyncMock()
        # Always fail
        mock_scanner.start.side_effect = Exception("Bluetooth permanently broken")
        
        test_mac = os.getenv('TEST_DEVICE_MAC', "00:00:00:00:00:00")
        flags = Flags(daemon_mode=False, file_logging=False, verbose=True)
        monitor = DeviceMonitor(test_mac, True, flags)
        monitor.scanner = mock_scanner
        
        # Mock _is_screen_locked
        monitor._is_screen_locked = MagicMock(side_effect=[True, False])
        
        # Mock asyncio.sleep
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # The method catches the exception, so we don't expect it to raise.
            # Instead, we verify it tried 5 times.
            await monitor._handle_screen_lock()
            
            # Verify start was called 5 times (max_retries)
            self.assertEqual(mock_scanner.start.call_count, 5)
            print("✓ Retry logic worked: Gave up after 5 attempts as expected.")

if __name__ == '__main__':
    unittest.main()
