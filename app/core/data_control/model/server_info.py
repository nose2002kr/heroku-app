from core.data_control.model import Model

class ServerInfo(Model):
    server_name: str
    survival_check: str

    def __hash__(self):
        return hash((self.server_name, self.survival_check))
    
    def get_name():
        return 'server_info_2'
