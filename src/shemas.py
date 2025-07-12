from datetime import date, time
from typing import Dict, List, Tuple

from pydantic import BaseModel, ConfigDict, TypeAdapter


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={"serialize_none": True},
    )


class Slot(BaseSchema):
    date: date
    start: time
    end: time

    def __str__(self) -> str:
        return f"{self.date} {self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"


class Day(Slot):
    id: int


class TimeSlot(BaseSchema):
    day_id: int
    start: time
    end: time

    def __str__(self) -> str:
        return f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"


class RawTimeSlot(TimeSlot):
    id: int


class RawTimeData(BaseSchema):
    days: List[Day]
    timeslots: List[RawTimeSlot]


TimeSlotList = TypeAdapter(List[TimeSlot])

ScheduleType = Dict[str, Tuple[Day, List[TimeSlot]]]
Schedule = TypeAdapter(ScheduleType)

