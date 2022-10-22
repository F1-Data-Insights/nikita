import asyncio
import os
import logging
from pandas import DataFrame
from dotenv import load_dotenv
import fastf1 as ff1
from nikita.mongo import connect_mongo_client
from nikita.mongo.models import Event, Lap, Telemetry

load_dotenv()

MONGODB_URI = os.getenv("mongodb_url")


def setup_ff1():
    if not os.path.exists("cache"):
        os.makedirs("cache")
    ff1.Cache.enable_cache("cache")


async def populate_telemetry(event_id: str, lap_id: str, telemetry: DataFrame):
    """Populate telemetry"""
    telemetry = telemetry.drop(['Date'], axis=1)
    telemetry = telemetry.dropna()
    telemetry['TimeSeconds'] = telemetry.Time.dt.total_seconds()

    for idx, row in telemetry.iterrows():
        telemetry = Telemetry(
            rpm=int(row.RPM),
            speed=float(row.Speed),
            gear=int(row.nGear),
            throttle=int(row.Throttle),
            brake=bool(row.Brake),
            drs=int(row.DRS),
            time=float(row.TimeSeconds),
            distance=float(row.Distance),
            lap=lap_id,
            event=event_id,
        )
        await telemetry.insert()

async def populate_laps(event_id: str, laps: DataFrame):
    """Populate laps for a given event, loads also the telemetry data for the single lap"""
    laps = laps.drop(['PitInTime', 'PitOutTime', 'IsAccurate'], axis=1)
    laps = laps.dropna()

    laps['LapTimeSeconds'] = laps.LapTime.dt.total_seconds()
    laps['Sector1TimeSeconds'] = laps.Sector1Time.dt.total_seconds()
    laps['Sector2TimeSeconds'] = laps.Sector2Time.dt.total_seconds()
    laps['Sector3TimeSeconds'] = laps.Sector3Time.dt.total_seconds()

    for idx, row in laps.iterrows():
        lap = Lap(
            lap_time=float(row.LapTimeSeconds),
            driver_number=int(row.DriverNumber),
            driver=row.Driver,
            lap_number=int(row.LapNumber),
            sector_1_time=float(row.Sector1TimeSeconds),
            sector_2_time=float(row.Sector2TimeSeconds),
            sector_3_time=float(row.Sector3TimeSeconds),
            compound=row.Compound,
            event=event_id,
        )
        await lap.insert()
        telemetry = row.get_car_data().add_distance()
        logging.info(f"Processing telemetry for lap {idx}")
        await populate_telemetry(event_id, lap.id, telemetry)


async def create_event(_year: int, _round: str, _session: str):
    session = ff1.get_session(_year, _round, _session)
    session.load()
    event = Event(year=_year, session=_session, round=_round)
    await event.insert()
    return session, event.id


async def main():
    setup_ff1()
    await connect_mongo_client(MONGODB_URI)

    session, event_id = await create_event(2022, "Bahrain", "R")
    await populate_laps(event_id, session.laps)

    logging.info("Sleeping...")
    while True:
        await asyncio.sleep(5)
