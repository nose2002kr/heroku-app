from app.core.data_control import ServerCommandInfoDataControl, ServerInfoDataControl
from service.server_cli import request_to_proceed_commend_on_cli
from app.core.data_control.model.server_command_info import Protocol
from loguru import logger
from service.kafka_interface.kafka_message_consumer import KafkaMessageConsumer
from app.core.data_control import ServerPowerStatusInfoDataControl
from app.core.data_control.model.server_power_status_info import ServerPowerStatusInfo, PowerStatus
from app.core.data_control.model.server_info import ServerInfo
from app.core.data_control.model.server_command_info import ServerCommandInfo
from datetime import datetime

import aiohttp

class ServerMessageConsumer(KafkaMessageConsumer):
    def __init__(self):
        super().__init__('server')

    async def __check_server(self, server_info: ServerInfo):
        async with aiohttp.ClientSession() as session:
            logger.debug(server_info.survival_check)
            async with session.get(server_info.survival_check) as response:
                if response.status == 200:
                    self.notify_started(server_info.server_name, 'is alive')
                else:
                    self.notify_stopped(server_info.server_name, 'is dead')
    
    def notify_status(self, server_name: str, status: PowerStatus, modifier: str = None):
        logger.debug(f'{server_name} {modifier if modifier is not None else "is " + status.name.lower()}')
        ServerPowerStatusInfoDataControl().set(server_name,
                        ServerPowerStatusInfo(server_name=server_name, power_status=status, updated_at=datetime.now()))

    def notify_stopping(self, server_name: str, modifier: str = None): self.notify_status(server_name, PowerStatus.STOPPING, modifier)
    def notify_stopped (self, server_name: str, modifier: str = None): self.notify_status(server_name, PowerStatus.STOPPED , modifier)
    def notify_starting(self, server_name: str, modifier: str = None): self.notify_status(server_name, PowerStatus.STARTING, modifier)
    def notify_started (self, server_name: str, modifier: str = None): self.notify_status(server_name, PowerStatus.STARTED , modifier)

    def select_command(self, info: ServerCommandInfo, command: str):
        if command == 'turn_off':
            switch_command = info.path_of_turn_off
            notify_progressing = lambda: self.notify_stopping(info.server_name)
            notify_done = lambda: self.notify_stopped(info.server_name, 'is turned off')
        elif command == 'turn_on':
            switch_command = info.path_of_turn_on
            notify_progressing = lambda: self.notify_starting(info.server_name)
            notify_done = lambda: self.notify_started(info.server_name, 'is turned on')
        else:
            logger.debug(f'command {command} is not supported')
            return None
        return switch_command, notify_progressing, notify_done

    async def consume(self):
        try:
            logger.debug('consumer start')
            await self.consumer.start()
            logger.debug('consumer started')

            # Consume messages
            async for raw_msg in self.consumer:
                try:
                    msg = raw_msg.value.decode('utf-8')
                    logger.debug(f"consumed: {msg}")
                    server,command = msg.split(':')

                    info = ServerCommandInfoDataControl().take(server)
                    server_info = ServerInfoDataControl().take(server)

                    logger.debug(f'check if server is alive, before switching power status: {server_info.server_name}')
                    await self.__check_server(server_info)

                    if info.protocol.value == Protocol.CLI.value:
                        restore_point = ServerPowerStatusInfoDataControl().take(server)
                        command, progressing, done = self.select_command(info, command)

                        progressing()
                        try:
                            await request_to_proceed_commend_on_cli( 
                                            command_line=command,
                                            progressFn=None,
                                            wrapUpFn=None)
                        except:
                            logger.exception('error occurred while executing command')
                            ServerPowerStatusInfoDataControl().set(server, restore_point)
                        else:
                            done()
                    else:
                        logger.debug(f'protocol {info.protocol} is not supported')
                except:
                    logger.exception('error occurred')
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            logger.debug('consumer stopped')
            await self.consumer.stop()
