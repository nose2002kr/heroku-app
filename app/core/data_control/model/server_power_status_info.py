from core.data_control.model import Model
from enum import Enum

class PowerStatus(Enum):
    STARTING = 0
    STARTED  = 1
    STOPPING = 2
    STOPPED  = 3

class ServerPowerStatusInfo(Model):
    server_name: str
    power_status: PowerStatus

    def __hash__(self):
        return hash((
            self.server_name,
            self.power_status
        ))
    
    def get_name():
        return 'server_power_status_info_2'
