import pytest
import sys
from unittest.mock import patch, MagicMock
from brios.cli import main, Application
from typing import Any, Generator


@pytest.fixture
def mock_service_manager() -> Generator[MagicMock, None, None]:
    with patch("brios.cli.ServiceManager") as MockSM:
        yield MockSM


def test_stop_default(mock_service_manager: MagicMock) -> None:
    with patch("sys.argv", ["brios", "--stop"]):
        main()
        mock_instance = mock_service_manager.return_value
        mock_instance.stop.assert_called_once()


def test_stop_hours(mock_service_manager: MagicMock) -> None:
    with patch("sys.argv", ["brios", "--stop", "2"]):
        main()
        mock_instance = mock_service_manager.return_value
        mock_instance.pause.assert_called_with(2)


def test_stop_invalid_hours(
    mock_service_manager: MagicMock, capsys: Any
) -> None:
    with patch("sys.argv", ["brios", "--stop", "25"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1


def test_stop_invalid_string(
    mock_service_manager: MagicMock, capsys: Any
) -> None:
    with patch("sys.argv", ["brios", "--stop", "foo"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1


def test_stop_day(mock_service_manager: MagicMock) -> None:
    with patch("sys.argv", ["brios", "--stop", "-d"]):
        main()
        mock_instance = mock_service_manager.return_value
        mock_instance.pause.assert_called_with(24)


def test_stop_week(mock_service_manager: MagicMock) -> None:
    with patch("sys.argv", ["brios", "--stop", "-w"]):
        main()
        mock_instance = mock_service_manager.return_value
        mock_instance.pause.assert_called_with(168)


def test_day_without_stop(mock_service_manager: MagicMock) -> None:
    with patch("sys.argv", ["brios", "-d"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 2  # argparse error code


def test_week_without_stop(mock_service_manager: MagicMock) -> None:
    with patch("sys.argv", ["brios", "-w"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 2
