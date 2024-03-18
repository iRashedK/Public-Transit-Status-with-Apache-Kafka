"""Defines trends calculations for stations"""
import logging

import faust

logger = logging.getLogger(__name__)

BROKER_URL = "kafka://localhost:9092,kafka://localhost:9093,kafka://localhost:9094"
# BROKER_URL = "kafka://kafka0:9092,kafka://kafka1:9093,kafka://kafka1:9094"


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


app = faust.App("stations-stream", broker=BROKER_URL, store="memory://")
topic = app.topic("kc-postgres-stations", value_type=Station)
out_topic = app.topic("org.chicago.cta.stations.table.v1", value_type=TransformedStation, partitions=1)
table = app.Table(
    name="trx_stations_table",
    default=int,
    partitions=1,
    changelog_topic=out_topic,
)


@app.agent(topic)
async def transform_station(stations):
    async for station in stations:
        line_color = ""
        if station.red:
            line_color = "red"
        elif station.blue:
            line_color = "red"
        elif station.green:
            line_color = "green"

        table[station.station_id] = TransformedStation(station_id=station.station_id,
                                                       station_name=station.station_name,
                                                       order=station.order,
                                                       line=line_color)


if __name__ == "__main__":
    app.main()
