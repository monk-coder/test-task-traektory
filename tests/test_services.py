import pytest
from datetime import time
from unittest import mock

from src.services import check_slot, show_busy, find_free_slots, find_slot
from src.shemas import TimeSlot


# Slot checking tests
@pytest.mark.parametrize(
    "slot_str,expected_message",
    [
        ("2024-10-10 14:00-15:00", "The slot can be scheduled at the selected time"),
        ("2024-10-10 11:00-12:00", "Sorry, slot"),
    ]
)
def test_check_slot_scenarios(slot_str, expected_message, mock_request_data, capsys):
    check_slot(slot_str)
    captured = capsys.readouterr()
    assert expected_message in captured.out


@pytest.mark.parametrize(
    "invalid_input",
    [
        "invalid date",
        "2024-13-45 11:00-12:00",
        "2024-10-10 25:00-26:00",
    ]
)
def test_check_slot_invalid_inputs(invalid_input, mock_request_data, capsys):
    check_slot(invalid_input)
    captured = capsys.readouterr()
    assert "ERROR:" in captured.out


def test_check_slot_no_available_slots(capsys):
    with mock.patch("src.services.format_data", return_value={}):
        check_slot("2024-12-31 11:00-12:00")
        captured = capsys.readouterr()
        assert "Sorry, no slots are available for the selected date." in captured.out


# Show busy slots tests
def test_show_busy_successful(mock_request_data, mock_display_schedule):
    show_busy()
    mock_display_schedule.assert_called_once()
    assert mock_display_schedule.call_args is not None


def test_show_busy_handles_errors(monkeypatch, capsys):
    monkeypatch.setattr("src.services.request_data", mock.Mock(side_effect=Exception("Test error")))
    show_busy()
    captured = capsys.readouterr()
    assert "ERROR:" in captured.out


# Find free slots tests
@pytest.mark.parametrize(
    "date_str,expected_result",
    [
        ("2024-10-10", [
            TimeSlot(day_id=1, start=time(9, 0), end=time(11, 0)),
            TimeSlot(day_id=1, start=time(12, 0), end=time(18, 0))
        ]),
        ("2024-12-31", []),
    ]
)
def test_find_free_slots(date_str, expected_result, mock_request_data, formatted_schedule):
    with mock.patch("src.services.format_data", return_value=formatted_schedule):
        slots = find_free_slots(date_str)
        print(slots)
        if expected_result:
            assert all(isinstance(slot, TimeSlot) for slot in slots)
        else:
            assert not slots


def test_find_free_slots_invalid_date(mock_request_data):
    result = find_free_slots("invalid-date")
    assert result is None


# Find slot tests
@pytest.mark.parametrize(
    "duration_str,expected_output",
    [
        ("01:00", "Suitable free slots"),
        ("10:00", "No suitable free slots found."),
    ]
)
def test_find_slot(duration_str, expected_output, mock_request_data, formatted_schedule, capsys):
    with mock.patch("src.services.format_data", return_value=formatted_schedule):
        find_slot(duration_str)
        captured = capsys.readouterr()
        assert expected_output in captured.out


def test_find_slot_invalid_duration(mock_request_data, capsys):
    find_slot("invalid")
    captured = capsys.readouterr()
    assert "ERROR:" in captured.out
