from service.kafka_interface.kafka_message_producer import KafkaMessageProducer

class ServerMessageProducer(KafkaMessageProducer):
    def __init__(self):
        super().__init__('server')
