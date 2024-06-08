from kafka import KafkaProducer

class ServiceMessageProducer:
    def __init__(self, kafka_server: str):
        print(kafka_server)
        self.producer = KafkaProducer(api_version=(3,7,0),bootstrap_servers=kafka_server)
        self.topic = 'server'

    def send(self, message: str):
        self.producer.send(self.topic, message.encode())
        self.producer.flush()
