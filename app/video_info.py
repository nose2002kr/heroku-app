from pydantic import BaseModel

class VideoInfo(BaseModel):
    project_name: str
    description: str
    video_link: str

    def __hash__(self):
        return hash((self.project_name, self.description, self.video_link))
    