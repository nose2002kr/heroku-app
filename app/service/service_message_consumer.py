from data_control import ServerCommandInfoDataControl, ServerInfoDataControl
from service.server_cli import request_to_proceed_commend_on_cli
from app.core.data_control.model.server_command_info import Protocol
from loguru import logger
from service.kafka_interface.kafka_message_consumer import KafkaMessageConsumer
from data_control import ServerPowerStatusInfoDataControl
from app.core.data_control.model.server_power_status_info import ServerPowerStatusInfo, PowerStatus

import aiohttp

class ServiceMessageConsumer(KafkaMessageConsumer):
    def __init__(self):
        super().__init__('server')

    async def consume(self):
        
        try:
            logger.debug('consumer start')
            await self.consumer.start()
            logger.debug('consumer started')

            # Consume messages
            async for raw_msg in self.consumer:
                try:
                    msg = raw_msg.value.decode('utf-8')
                    server,command = msg.split(':')
                    logger.debug(f"consumed: {server} {command}")

                    info = ServerCommandInfoDataControl().take(server)
                    server_info = ServerInfoDataControl().take(server)

                    logger.debug(f'check if server is alive, before switching power status: {server_info.server_name}')
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(server_info.survival_check) as response:
                            if response.status == 200:
                                logger.debug(f'{server_info.server_name} is alive')
                                ServerPowerStatusInfoDataControl().set(server,
                                            ServerPowerStatusInfo(server_name=server, power_status=PowerStatus.STARTED))
                                
                            else:
                                logger.debug(f'{server_info.server_name} is dead')
                                ServerPowerStatusInfoDataControl().set(server, 
                                            ServerPowerStatusInfo(server_name=server, power_status=PowerStatus.STOPPED))

                    if info.protocol.value == Protocol.CLI.value:
                        switch_command: str = ''
                        progressive: PowerStatus
                        perfect: PowerStatus
                        sentence: str = ''
                        if command == 'turn_off':
                            switch_command = info.path_of_turn_off
                            progressive = PowerStatus.STOPPING
                            perfect = PowerStatus.STOPPED
                            sentence = f'{server} is turned off'
                        elif command == 'turn_on':
                            switch_command = info.path_of_turn_on
                            progressive = PowerStatus.STARTING
                            perfect = PowerStatus.STARTED
                            sentence = f'{server} is turned on'
                        else:
                            logger.debug(f'command {command} is not supported')
                            continue
                        
                        prev_status = ServerPowerStatusInfoDataControl().take(server)
                        ServerPowerStatusInfoDataControl().set(server,
                                    ServerPowerStatusInfo(server_name=server, power_status=progressive))
                        try:
                            await request_to_proceed_commend_on_cli( 
                                            command_line=switch_command,
                                            progressFn=None,
                                            wrapUpFn=None)
                        except:
                            logger.exception('error occurred while executing command')
                            ServerPowerStatusInfoDataControl().set(server, prev_status)
                            
                        ServerPowerStatusInfoDataControl().set(server, 
                                    ServerPowerStatusInfo(server_name=server, power_status=perfect))
                        logger.debug(sentence)
                    else:
                        logger.debug(f'protocol {info.protocol} is not supported')
                except:
                    logger.exception('error occurred')
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            logger.debug('consumer stopped')
            await self.consumer.stop()
