import os
import redis
from config import Config

from video_info import VideoInfo
from servers_info import ServersInfo

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
        

class ServersInfoDataControl:
    def take_servers_infos() -> set[ServersInfo]:
        raw_sets = __redis__.smembers('servers_info')
        datas = set[ServersInfo]()
        for raw in raw_sets:
            datas.add(ServersInfo.model_validate_json(raw))
        return datas

    def add_servers_info(info: ServersInfo):
        __redis__.sadd('servers_info', info.model_dump_json())
        
    def remove_servers_info(info: ServersInfo):
        __redis__.srem('servers_info', info.model_dump_json())
        