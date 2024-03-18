"""Creates a turnstile data producer"""
import logging
from pathlib import Path

from confluent_kafka import avro

from .producer import Producer
from .turnstile_hardware import TurnstileHardware


logger = logging.getLogger(__name__)


class Turnstile(Producer):
    topic_name = "org.chicago.cta.turnstiles.v1"
    key_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/turnstile_key.json")
    value_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/turnstile_value.json")

    def __init__(self, station):
        """Create the Turnstile"""
        super().__init__(
            topic_name=Turnstile.topic_name,
            key_schema=Turnstile.key_schema,
            value_schema=Turnstile.value_schema,
            num_partitions=1,
            num_replicas=1,
        )
        self.station = station
        self.turnstile_hardware = TurnstileHardware(station)

    def run(self, timestamp, time_step):
        """Simulates riders entering through the turnstile."""
        num_entries = self.turnstile_hardware.get_entries(timestamp, time_step)
        # logger.info("turnstile kafka integration incomplete - skipping")
        try:
            for _ in range(num_entries):
                self.producer.produce(
                    topic=self.topic_name,
                    key={"timestamp": self.time_millis()},
                    value={
                        "station_id": self.station.station_id,
                        "station_name": self.station.station_name,
                        "line": self.station.color.name
                    },
                )
        except Exception as e:
            logger.info(f"failed to producer data for topic {self.topic_name}:\n{e}")
