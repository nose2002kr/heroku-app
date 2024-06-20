from kafka import KafkaProducer
from core.singleton import Singleton
from loguru import logger
from config import Config

class KafkaMessageProducer(metaclass=Singleton):
    def __init__(self, topic: str):
        self.topic = topic
        self.server = Config.kafka_host
        self.producer = KafkaProducer(api_version=(3,7,0),bootstrap_servers=self.server)
        logger.debug(f'connnected to {self.server}')

    async def send(self, message: str):
        logger.debug(f'send to {self.server}: {message}')
        self.producer.send(self.topic, message.encode())
        self.producer.flush()