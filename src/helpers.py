import functools
from datetime import date as dt_date, time as dt_time, timedelta
from datetime import datetime
from typing import Any, Callable, List, Union

import requests

from src.shemas import Day, RawTimeData, Schedule, ScheduleType, Slot, TimeSlot, TimeSlotList


def exception_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that wraps a function to handle exceptions gracefully.

    Args:
        func (Callable[..., Any]): The function to be wrapped.

    Returns:
        Callable[..., Any]: The wrapped function that handles exceptions.
    """
    @functools.wraps(func)
    def _wraps(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"ERROR: {e}")

    return _wraps


def request_data() -> RawTimeData:
    """
    Fetches schedule data from the API endpoint.

    Returns:
        RawTimeData: Validated schedule data from the API.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
        ValueError: If the received data is invalid.
        Exception: For any other unexpected errors.
    """
    data = requests.get("https://ofc-test-01.tspb.su/test-task/", timeout=5)

    if data.status_code != 200:
        raise requests.exceptions.RequestException("Failed to retrieve data.")

    try:
        return RawTimeData.model_validate(data.json())
    except (requests.exceptions.JSONDecodeError, ValueError) as e:
        raise ValueError("Received invalid schedule data.") from e
    except Exception as e:
        raise Exception("An unknown error occurred while requesting schedule data.") from e


def format_data(raw_data: RawTimeData) -> ScheduleType:
    """
    Formats and validates raw schedule data into a structured schedule.

    Args:
        raw_data (RawTimeData): The raw schedule data to format.

    Returns:
        ScheduleType: A validated schedule dictionary.

    Raises:
        TypeError: If the input data is not of type RawTimeData.
    """
    if not isinstance(raw_data, RawTimeData):
        raise TypeError("Invalid data type.")

    data = {}

    sorted_days = sorted(raw_data.days, key=lambda x: x.date)

    for day in sorted_days:
        date = day.date.strftime("%Y-%m-%d")

        timeslots = filter(lambda x: x.day_id == day.id, raw_data.timeslots)
        sorted_timeslots = sorted(timeslots, key=lambda x: x.start)

        data[date] = (day, TimeSlotList.validate_python(sorted_timeslots))

    return Schedule.validate_python(data)


def parse_slot_input(slot: str) -> Slot:
    """
    Parses a string input into a Slot object.

    Args:
        slot (str): A string in the format 'YYYY-MM-DD HH:MM-HH:MM'.

    Returns:
        Slot: A validated Slot object containing date and time information.

    Raises:
        ValueError: If the input string format is invalid.
    """
    try:
        _date, *time = slot.strip().split()

        if len(time) == 1:
            time = time[0].split("-")

        date = datetime.strptime(_date.strip(), "%Y-%m-%d")
        start = datetime.strptime(time[0], "%H:%M").time()
        end = datetime.strptime(time[-1], "%H:%M").time()
    except ValueError as e:
        raise ValueError(
            "Invalid slot format. Provide a date and a time range in the format: 'YYYY-MM-DD HH:MM-HH:MM'."
        ) from e

    if start >= end:
        raise ValueError("Start time must be before end time")

    return Slot(date=date, start=start, end=end)


def duration_str_to_timedelta(duration_str: str) -> timedelta:
    """
    Converts a duration string to a timedelta object.

    Args:
        duration_str (str): Duration string in the format 'HH:MM'.

    Returns:
        timedelta: A timedelta object representing the duration.
    """
    hours, minutes = map(int, duration_str.strip().split(":"))
    return timedelta(hours=hours, minutes=minutes)


def free_slots_at_date(schedule: ScheduleType, date_key: dt_date) -> List[TimeSlot]:
    """
    Finds available time slots for a given date in the schedule.

    Args:
        schedule (ScheduleType): The schedule to search in.
        date_key (dt_date): The date to find free slots for.

    Returns:
        List[TimeSlot]: A list of available time slots for the given date.

    Raises:
        TypeError: If the date_key is not of type dt_date.
    """
    Schedule.validate_python(schedule)

    if not isinstance(date_key, dt_date):
        raise TypeError("Invalid date key type.")

    str_date = date_key.strftime("%Y-%m-%d")

    if schedule.get(str_date) is None:
        return []

    day = schedule[str_date][0].model_copy(deep=True)

    free_slots = []
    for slot in schedule[str_date][1]:
        if day.start == slot.start:
            day.start = slot.end
        elif day.start < slot.start:
            free_slots.append(TimeSlot(day_id=slot.day_id, start=day.start, end=slot.start))
            day.start = slot.end

    if day.start != day.end:
        free_slots.append(TimeSlot(day_id=day.id, start=day.start, end=day.end))

    return free_slots


def find_suitable_slot(schedule: ScheduleType, duration: timedelta) -> ScheduleType:
    """
    Finds a suitable slot for the given duration in the schedule.

    Args:
        schedule (ScheduleType): The schedule to search in.
        duration (timedelta): The duration for which a slot is needed.

    Returns:
        ScheduleType: A schedule containing the suitable slot.

    Raises:
        TypeError: If the schedule is not of type dict.
        ValueError: If the duration is not a positive timedelta.
    """
    if not isinstance(schedule, dict):
        raise TypeError("Invalid schedule type.")

    Schedule.validate_python(schedule)

    if not isinstance(duration, timedelta) or duration.total_seconds() <= 0:
        raise ValueError("Invalid duration. Must be a positive timedelta.")

    suitable_schedule = {}

    for key in schedule:
        _date = datetime.strptime(key, "%Y-%m-%d").date()
        free_slots = free_slots_at_date(schedule, _date)
        suitable_slots = list(filter(lambda x: time_diff(x.end, x.start) >= duration, free_slots))
        if not suitable_slots:
            continue
        suitable_schedule[key] = (schedule[key][0], suitable_slots)

    return Schedule.validate_python(suitable_schedule)


def check_time_boundaries(slot: Slot, other: Union[Day, TimeSlot]) -> bool:
    """
    Checks if a slot is within the time boundaries of a day or another slot.

    Args:
        slot (Slot): The slot to check.
        other (Union[Day, TimeSlot]): The day or slot to check against.

    Returns:
        bool: True if the slot is within boundaries, False otherwise.

    Raises:
        TypeError: If the other parameter is not of type Day or TimeSlot.
    """
    if not isinstance(other, (Day, TimeSlot)):
        raise TypeError(f"Invalid type for 'other'. Expected Day or TimeSlot, got {type(other)}. {other}")
    return other.start <= slot.start and slot.end <= other.end


def time_diff(time_1: dt_time, time_2: dt_time) -> timedelta:
    """
    Calculates the difference between two time objects.

    Args:
        time_1 (dt_time): The first time object.
        time_2 (dt_time): The second time object.

    Returns:
        timedelta: The difference between the two times.
    """
    dt1 = datetime.combine(dt_date.min, time_1)
    dt2 = datetime.combine(dt_date.min, time_2)
    return dt1 - dt2


def can_schedule_slot(slot: Slot, free_slots: List[TimeSlot]) -> bool:
    """
    Determines if a slot can be scheduled within the available free slots.

    Args:
        slot (Slot): The slot to schedule.
        free_slots (List[TimeSlot]): The list of available free slots.

    Returns:
        bool: True if the slot can be scheduled, False otherwise.
    """
    if not free_slots:
        return False
    return any(check_time_boundaries(slot, free_slot) for free_slot in free_slots)


def display_schedule(schedule: ScheduleType, title: str = "", skip_empty: bool = False) -> None:
    """
    Displays the schedule in a readable format.

    Args:
        schedule (ScheduleType): The schedule to display.
        title (str, optional): An optional title for the schedule. Defaults to "".
        skip_empty (bool, optional): Whether to skip days with no available slots. Defaults to False.

    Raises:
        ValueError: If the schedule is empty or not valid.
    """
    if not schedule:
        raise ValueError("No schedule found.")

    Schedule.validate_python(schedule)

    if title:
        print(f"\n{title:-^40}\n")
    else:
        print(f"\n{'-' * 40}\n")

    for day, day_data in schedule.items():
        if not day_data[1] and skip_empty:
            if not skip_empty:
                print(f"{day}:\n\tNo slots available for this day.")
            continue
        print(f"{day}:")
        for slot in day_data[1]:
            print(f"\t{slot.start.strftime('%H:%M')} - {slot.end.strftime('%H:%M')}")
    print(f"\n{'-' * 40}\n")
