"""Contains functionality related to Weather"""
import logging


logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 70.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        try:
            logger.info(f"message from weather!: {message}")
            self.temperature = message.value()['temperature']
            self.status = message.value()['status']
        except Exception as e:
            logger.info(f"failed to process weather message: {e}")
