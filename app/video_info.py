from pydantic import BaseModel

class VideoInfo(BaseModel):
    project_name: str
    video_link: str

    def __hash__(self):
        return hash((self.project_name, self.video_link))
    