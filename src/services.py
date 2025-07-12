from datetime import datetime
from typing import List, Optional

from src.helpers import (
    can_schedule_slot,
    display_schedule,
    duration_str_to_timedelta, exception_handler,
    find_suitable_slot,
    format_data,
    free_slots_at_date,
    parse_slot_input,
    request_data,
)
from src.shemas import ScheduleType, TimeSlot


@exception_handler
def check_slot(raw_slot: str) -> bool:
    """
    Checks if a given time slot is available for scheduling.

    Args:
        raw_slot (str): A string representing the slot in format 'YYYY-MM-DD HH:MM-HH:MM'.

    Returns:
        None: Prints the availability status of the slot.
    """
    slot = parse_slot_input(raw_slot)
    if slot is None:
        return False

    raw_schedule = request_data()
    schedule = format_data(raw_schedule)
    free_slots = free_slots_at_date(schedule, slot.date)

    if not free_slots:
        print("Sorry, no slots are available for the selected date.")
        return False

    if can_schedule_slot(slot, free_slots):
        print("The slot can be scheduled at the selected time.")
        return True

    print(f"Sorry, slot {slot} is unavailable.")
    return False


@exception_handler
def show_busy() -> ScheduleType:
    """
    Displays all busy time slots in the schedule.

    Returns:
        None: Prints the schedule of busy slots.
    """
    raw_time_data = request_data()
    schedule = format_data(raw_time_data)
    display_schedule(schedule, title="Busy slots")
    return schedule


@exception_handler
def find_free_slots(raw_date: str) -> Optional[List[TimeSlot]]:
    """
    Finds and displays all free time slots for a given date.

    Args:
        raw_date (str): A date string in the format 'YYYY-MM-DD'.

    Returns:
        None: Prints the available free slots for the specified date.
    """
    date = datetime.strptime(raw_date.strip(), "%Y-%m-%d").date()
    raw_time_data = request_data()
    schedule = format_data(raw_time_data)
    free_slots = free_slots_at_date(schedule, date)

    if free_slots:
        display_schedule({raw_date: (schedule[raw_date][0], free_slots)}, title="Free slots")
        return free_slots

    print(f"No free slots available on {raw_date}.")
    return None

@exception_handler
def find_slot(raw_duration: str) -> Optional[ScheduleType]:
    """
    Finds suitable slots for a given duration in the schedule.

    Args:
        raw_duration (str): Duration string in the format 'HH:MM'.

    Returns:
        None: Prints all suitable slots that can accommodate the specified duration.
    """
    duration = duration_str_to_timedelta(raw_duration)
    raw_time_data = request_data()
    schedule = format_data(raw_time_data)
    suitable_slots = find_suitable_slot(schedule, duration)

    if len(suitable_slots.values()) > 0:
        display_schedule(suitable_slots, title="Suitable free slots", skip_empty=True)
        return suitable_slots

    print("No suitable free slots found.")
    return None