import pytest
from datetime import date, time, timedelta
import requests
from unittest import mock

from src.helpers import (
    check_time_boundaries,
    duration_str_to_timedelta,
    exception_handler,
    find_suitable_slot,
    format_data,
    parse_slot_input,
    request_data,
    time_diff,
)
from src.shemas import Day, Slot


# Exception handling tests
@pytest.mark.parametrize(
    "test_func,expected_output",
    [
        (lambda: 1 / 0, "ERROR: division by zero"),
        (lambda: int("not a number"), "ERROR: invalid literal for int() with base 10: 'not a number'"),
    ],
)
def test_exception_handler(test_func, expected_output, capsys):
    exception_handler(test_func)()
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_output


def test_execute_function_without_exception():
    assert exception_handler(lambda: 1 / 1)() == 1


# Request data tests
class TestRequestData:
    def test_fetch_data_successfully(self, raw_time_data, mock_response, monkeypatch):
        mock_resp = mock_response(json_data=raw_time_data.model_dump())
        monkeypatch.setattr(requests, "get", mock.Mock(return_value=mock_resp))
        assert request_data() == raw_time_data

    def test_handle_http_error(self, mock_response, monkeypatch):
        mock_resp = mock_response(status=404)
        monkeypatch.setattr(requests, "get", mock.Mock(return_value=mock_resp))
        with pytest.raises(requests.exceptions.RequestException):
            request_data()

    def test_handle_request_timeout(self, monkeypatch):
        monkeypatch.setattr(requests, "get", mock.Mock(side_effect=requests.exceptions.Timeout))
        with pytest.raises(requests.exceptions.Timeout):
            request_data()


# Data formatting and parsing tests
def test_format_valid_data(raw_time_data):
    result = format_data(raw_time_data)
    assert isinstance(result, dict)


@pytest.mark.parametrize(
    "invalid_input,expected_error",
    [
        (1, TypeError),
        (None, TypeError),
        ("invalid", TypeError),  # Changed from {} to "invalid" as format_data expects RawTimeData
    ]
)
def test_format_invalid_data(invalid_input, expected_error):
    with pytest.raises(expected_error):
        format_data(invalid_input)


@pytest.mark.parametrize(
    "input_str,expected_result",
    [
        ("2024-10-10 14:00-15:00", Slot(date=date(2024, 10, 10), start=time(14, 0), end=time(15, 0))),
    ]
)
def test_parse_valid_slot_input(input_str, expected_result):
    assert parse_slot_input(input_str) == expected_result


@pytest.mark.parametrize(
    "invalid_input",
    [
        "2024-10-10 14:00",  # Missing end time
        "invalid",  # Completely invalid format
        "2024-13-45 14:00-15:00",  # Invalid date
        "",  # Empty string
    ]
)
def test_parse_slot_input_invalid_format(invalid_input):
    with pytest.raises(ValueError):
        parse_slot_input(invalid_input)


@pytest.mark.parametrize(
    "duration_str,expected_result",
    [
        ("02:30", timedelta(hours=2, minutes=30)),
        ("00:45", timedelta(minutes=45)),
    ]
)
def test_duration_str_to_timedelta(duration_str, expected_result):
    assert duration_str_to_timedelta(duration_str) == expected_result


def test_time_diff():
    assert time_diff(time(14, 30), time(12, 15)) == timedelta(hours=2, minutes=15)


# Time boundary tests
@pytest.mark.parametrize(
    "slot_time,boundary,expected",
    [
        ((10, 0, 11, 0), (9, 0, 18, 0), True),  # Within bounds
        ((9, 0, 18, 0), (9, 0, 18, 0), True),   # At boundaries
        ((8, 0, 19, 0), (9, 0, 18, 0), False),  # Outside bounds
    ]
)
def test_check_time_boundaries(slot_time, boundary, expected, test_day):
    slot = Slot(
        date=date(2024, 10, 10),
        start=time(slot_time[0], slot_time[1]),
        end=time(slot_time[2], slot_time[3])
    )
    day = Day(
        id=1,
        date=date(2024, 10, 10),
        start=time(boundary[0], boundary[1]),
        end=time(boundary[2], boundary[3])
    )
    assert check_time_boundaries(slot, day) is expected


def test_check_time_boundaries_invalid_type(test_slot):
    with pytest.raises(TypeError, match="Invalid type for 'other'"):
        check_time_boundaries(test_slot, "invalid")


# Slot finding tests
def test_find_suitable_slot(formatted_schedule):
    result = find_suitable_slot(formatted_schedule, timedelta(hours=1))
    assert isinstance(result, dict)


@pytest.mark.parametrize(
    "invalid_input,duration,expected_error,error_message",
    [
        ([], timedelta(hours=1), TypeError, "Invalid schedule type"),
        ({}, timedelta(seconds=-1), ValueError, "Invalid duration"),
    ]
)
def test_find_suitable_slot_invalid_inputs(invalid_input, duration, expected_error, error_message):
    with pytest.raises(expected_error, match=error_message):
        find_suitable_slot(invalid_input, duration)
