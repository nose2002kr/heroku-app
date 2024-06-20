from config import Config
from aiokafka import AIOKafkaConsumer
from core.singleton import Singleton

class KafkaMessageConsumer(metaclass=Singleton):
    def __init__(self, topic: str):
        self.server = Config.kafka_host
        self.topic = topic
        self.consumer = AIOKafkaConsumer(self.topic, bootstrap_servers=self.server)

    async def consume(self):
        pass
