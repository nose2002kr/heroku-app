from core.data_control.model import Model
from enum import Enum

class Protocol(Enum):
    CLI = 0
    HTTP = 1

class ServerCommandInfo(Model):
    server_name: str
    protocol: Protocol
    path_of_run: str
    path_of_turn_off: str
    path_of_turn_on: str
    path_of_log: str

    def __hash__(self):
        return hash((
            self.server_name,
            self.protocol,
            self.path_of_run,
            self.path_of_turn_off,
            self.path_of_turn_on,
            self.path_of_log,
        ))
    
    def get_name():
        return 'server_command_info_2'
