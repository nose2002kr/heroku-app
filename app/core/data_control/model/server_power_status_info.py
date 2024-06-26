from core.data_control.model import Model
from enum import Enum
from datetime import datetime

class PowerStatus(Enum):
    STARTING = 0
    STARTED  = 1
    STOPPING = 2
    STOPPED  = 3

class ServerPowerStatusInfo(Model):
    server_name: str
    power_status: PowerStatus
    updated_at: datetime

    def __hash__(self):
        return hash((
            self.server_name,
            self.power_status,
            self.updated_at
        ))
    
    def get_name():
        return 'server_power_status_info_2'
