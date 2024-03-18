"""Producer base-class providing common utilities and functionality"""
import logging
import time

from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer, CachedSchemaRegistryClient

logger = logging.getLogger(__name__)


class Producer:
    BROKER_URL = "PLAINTEXT://localhost:9092,PLAINTEXT://localhost:9093,PLAINTEXT://localhost:9094"
    # BROKER_URL = "PLAINTEXT://kafka0:9092,PLAINTEXT://kafka1:9093,PLAINTEXT://kafka1:9094"

    SCHEMA_REGISTRY_URL = "http://localhost:8081"
    # SCHEMA_REGISTRY_URL = "http://schema-registry:8081"

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
            self,
            topic_name,
            key_schema,
            value_schema=None,
            num_partitions=1,
            num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        self.broker_properties = {"bootstrap.servers": self.BROKER_URL}
        self.schema_registry = CachedSchemaRegistryClient({"url": self.SCHEMA_REGISTRY_URL})

        self.create_topic()
        self.producer = AvroProducer(config=self.broker_properties
                                     , schema_registry=self.schema_registry
                                     , default_key_schema=self.key_schema
                                     , default_value_schema=self.value_schema)

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        if self.topic_name not in Producer.existing_topics:
            try:
                admin_client = AdminClient(self.broker_properties)
                topic_list = [NewTopic(topic=self.topic_name, num_partitions=self.num_partitions, replication_factor=self.num_replicas)]
                admin_client.create_topics(topic_list)

                Producer.existing_topics.add(self.topic_name)
                logger.info(f"new topic created, {self.topic_name} ")
            except Exception as e:
                print(f"failed to create topic {self.topic_name}: {e}")

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        try:
            self.producer.flush()
            logger.info(f"producer for topic {self.topic_name} closed!")
        except Exception as e:
            logger.info(f"failed to close producer for topic {self.topic_name}: {e}")
