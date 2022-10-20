from beanie import Document, Indexed, Link
from typing import List

class Event(Document):
    year: Indexed(int)
    session: Indexed(str)
    round: Indexed(str)

class Lap(Document):
    lap_time: Indexed(int)
    driver_number: int
    driver: Indexed(str)
    lap_number : int
    sector_1_time: str
    sector_2_time: str
    sector_3_time: str
    compound: str
    event: Link('_id',Event)

class Telemetry(Document):
    rpm: int
    speed: int
    gear: int
    throttle : int
    brake: bool
    drs: int
    time: int
    distance: float
    lap: Link('_id',Lap)