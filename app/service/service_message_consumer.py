from data_control import ServerCommandInfoDataControl, ServerInfoDataControl
from service.server_cli import request_to_proceed_commend_on_cli
from app.core.data_control.model.server_command_info import Protocol
from loguru import logger
from service.kafka_interface.kafka_message_consumer import KafkaMessageConsumer
from data_control import ServerPowerStatusInfoDataControl
from app.core.data_control.model.server_power_status_info import ServerPowerStatusInfo, PowerStatus
import requests

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

                    info = ServerCommandInfoDataControl.get_server_command_info(server)
                    servers = ServerInfoDataControl().take_datas()
                    for server_info in servers:
                        if server_info.server_name != server:
                            continue
                        logger.debug(f'check if server is alive, before switching power status: {server_info.server_name}')
                        res = requests.get(server_info.survival_check)
                        if res.status_code == 200:
                            logger.debug(f'{server_info.server_name} is alive')
                            ServerPowerStatusInfoDataControl.set_server_power_status_info(server, 
                                        ServerPowerStatusInfo(server_name=server, power_status=PowerStatus.STARTED))
                            
                        else:
                            logger.debug(f'{server_info.server_name} is dead')
                            ServerPowerStatusInfoDataControl.set_server_power_status_info(server, 
                                        ServerPowerStatusInfo(server_name=server, power_status=PowerStatus.STOPPED))
                        break

                    if info.protocol == Protocol.CLI:
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
                        
                        prev_status = ServerPowerStatusInfoDataControl.get_server_power_status_info(server)
                        ServerPowerStatusInfoDataControl.set_server_power_status_info(server, 
                                    ServerPowerStatusInfo(server_name=server, power_status=progressive))
                        try:
                            await request_to_proceed_commend_on_cli( 
                                            command_line=switch_command,
                                            progressFn=None,
                                            wrapUpFn=None)
                        except:
                            logger.exception('error occurred while executing command')
                            ServerPowerStatusInfoDataControl.set_server_power_status_info(server, prev_status)
                            
                        ServerPowerStatusInfoDataControl.set_server_power_status_info(server, 
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
