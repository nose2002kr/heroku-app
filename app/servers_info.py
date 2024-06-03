from pydantic import BaseModel

class ServersInfo(BaseModel):
    server_name: str
    survival_check: str

    def __hash__(self):
        return hash((self.server_name, self.survival_check))
    