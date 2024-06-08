from config import Config
from aiokafka import AIOKafkaConsumer
from data_control import ServerCommandInfoDataControl
from service.server_cli import request_to_proceed_commend_on_cli
from server_command_info import Protocol

class ServiceMessageConsumer:
    async def consume(kafka_server: str):
        consumer = AIOKafkaConsumer('server', bootstrap_servers=kafka_server)
        
        # Get cluster layout and join group `my-group`
        await consumer.start()
        try:
            # Consume messages
            async for raw_msg in consumer:
                msg = raw_msg.value.decode('utf-8')
                server,command = msg.split(':')
                print(f"consumed: {server} {command}")
                #print("consumed: ", msg.topic, msg.partition, msg.offset,
                    #msg.key, msg.value, msg.timestamp)

                info = ServerCommandInfoDataControl.get_server_command_info(server)
                if info.protocol == Protocol.CLI:
                    await request_to_proceed_commend_on_cli( 
                                        command_line=info.path_of_turn_off if command == 'turn_off' else info.path_of_turn_on,
                                        progressFn=None,
                                        wrapUpFn=None)
                    print(f'{server} is turned off' if command == 'turn_off' else f'{server} is turned on')
                else:
                    print(f'protocol {info.protocol} is not supported')
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()
