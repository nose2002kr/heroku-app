import os
import redis
from config import Config

from video_info import VideoInfo

__redis__ = redis.Redis(host=Config.redis_host, port=Config.redis_port, password=Config.redis_pwd)

class VideoInfoDataControl:
    def take_video_infos() -> set[VideoInfo]:
        raw_sets = __redis__.smembers('video_info')
        datas = set[VideoInfo]()
        for raw in raw_sets:
            datas.add(VideoInfo.model_validate_json(raw))
        return datas

    def add_video_info(info: VideoInfo):
        __redis__.sadd('video_info', info.model_dump_json())
        
    def remove_video_info(info: VideoInfo):
        __redis__.srem('video_info', info.model_dump_json())
        