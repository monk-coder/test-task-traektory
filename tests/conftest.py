import pytest
from datetime import date, time
from unittest import mock
from src.shemas import RawTimeData, Slot, TimeSlot, Day

TEST_DATA = {
    "days": [
        {"id": 1, "date": "2024-10-10", "start": "09:00", "end": "18:00"},
        {"id": 2, "date": "2024-10-11", "start": "08:00", "end": "17:00"},
    ],
    "timeslots": [
        {"id": 1, "day_id": 1, "start": "11:00", "end": "12:00"},
        {"id": 3, "day_id": 2, "start": "09:30", "end": "16:00"},
    ],
}

@pytest.fixture
def raw_time_data():
    return RawTimeData(**TEST_DATA)

@pytest.fixture
def formatted_schedule():
    return {
        "2024-10-10": (
            Day(id=1, date=date(2024, 10, 10), start=time(9, 0), end=time(18, 0)),
            [TimeSlot(day_id=1, start=time(11, 0), end=time(12, 0))]
        ),
        "2024-10-11": (
            Day(id=2, date=date(2024, 10, 11), start=time(8, 0), end=time(17, 0)),
            [TimeSlot(day_id=2, start=time(9, 30), end=time(16, 0))]
        )
    }

@pytest.fixture
def sample_slots():
    return [
        Slot(date=date(2024, 10, 10), start=time(14, 0), end=time(15, 0)),
        Slot(date=date(2024, 10, 10), start=time(9, 0), end=time(10, 0)),
        Slot(date=date(2024, 10, 11), start=time(11, 0), end=time(12, 0)),
    ]

@pytest.fixture
def sample_time_slots():
    return [
        TimeSlot(day_id=1, start=time(9, 0), end=time(11, 0)),
        TimeSlot(day_id=1, start=time(12, 0), end=time(18, 0)),
    ]

@pytest.fixture
def test_slot():
    return Slot(date=date(2024, 10, 10), start=time(14, 0), end=time(15, 0))

@pytest.fixture
def test_day():
    return Day(id=1, date=date(2024, 10, 10), start=time(9, 0), end=time(18, 0))

@pytest.fixture
def mock_response():
    def _mock_response(status=200, json_data=None):
        mock_resp = mock.Mock()
        mock_resp.status_code = status
        mock_resp.json = mock.Mock(return_value=json_data)
        return mock_resp
    return _mock_response

@pytest.fixture
def mock_request_data(monkeypatch, raw_time_data):
    mock_func = mock.Mock(return_value=raw_time_data)
    monkeypatch.setattr("src.services.request_data", mock_func)
    return mock_func

@pytest.fixture
def mock_display_schedule(monkeypatch):
    mock_func = mock.Mock()
    monkeypatch.setattr("src.services.display_schedule", mock_func)
    return mock_func

__all__ = (
    "TEST_DATA",
    "raw_time_data",
    "sample_slots",
    "sample_time_slots",
    "test_slot",
    "test_day",
    "mock_response",
    "mock_request_data",
    "mock_display_schedule",
    "formatted_schedule"
)
