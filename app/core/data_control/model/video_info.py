from core.data_control.model.model import Model

class VideoInfo(Model):
    project_name: str
    description: str
    video_link: str

    def __hash__(self):
        return hash((self.project_name, self.description, self.video_link))
    
    def get_name():
        return 'video_info_2'
