import asyncio
import os
import logging
from dotenv import load_dotenv
import fastf1 as ff1
from nikita.mongo import connect_mongo_client
from nikita.mongo.models import Event, Lap, Telemetry

load_dotenv()

MONGODB_URI = os.getenv("mongodb_url")

async def populate_laps(session , event_id: str):
    pass


async def create_event(_year: int, _round:str, _session: str):
    session = ff1.get_session(_year, _round, _session)
    event = Event(year=_year, session=_session, round=_round)
    await event.insert()
    return session , event.id


async def main():
    await connect_mongo_client(MONGODB_URI)
    session, event_id = create_event(2022, "Bahrain", "R")

    logging.info(event_id)
    while True:
        asyncio.sleep(5)
        logging.info('Sleeping...')

