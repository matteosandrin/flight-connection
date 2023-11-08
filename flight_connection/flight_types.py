from dataclasses import dataclass
import math
from typing import Tuple


@dataclass
class Airport:
    iata_code: str
    name: str
    timezone: str
    location_name: str
    location: Tuple[float, float]


@dataclass
class Time:
    scheduled_sec: int
    actual_sec: int
    
    def delay_sec(self):
        return self.actual_sec - self.scheduled_sec


@dataclass
class Flight:
    origin: Airport
    destination: Airport
    start: Time
    end: Time


@dataclass
class Connection:
    start: Time
    end: Time

    def length_sec(self) -> int:
        return self.end.actual_sec - self.start.actual_sec

    def length_hours_mins(self) -> Tuple[int, int]:
        hours = math.floor(self.length_sec() / (60 * 60))
        mins = math.floor((self.length_sec() % (60 * 60)) / 60)
        return (hours, mins)
