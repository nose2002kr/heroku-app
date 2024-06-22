from pydantic import BaseModel
from enum import Enum

class PowerStatus(Enum):
    STARTING = 0
    STARTED  = 1
    STOPPING = 2
    STOPPED  = 3

class ServerPowerStatusInfo(BaseModel):
    server_name: str
    power_status: PowerStatus

    def __hash__(self):
        return hash((
            self.server_name,
            self.power_status
        ))
    