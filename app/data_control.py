import redis
from config import Config

from video_info import VideoInfo
from server_info import ServerInfo
from server_command_info import ServerCommandInfo

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
        

class ServerInfoDataControl:
    def take_server_infos() -> set[ServerInfo]:
        raw_sets = __redis__.smembers('server_info')
        datas = set[ServerInfo]()
        for raw in raw_sets:
            datas.add(ServerInfo.model_validate_json(raw))
        return datas

    def add_server_info(info: ServerInfo):
        __redis__.sadd('server_info', info.model_dump_json())
        
    def remove_server_info(info: ServerInfo):
        __redis__.srem('server_info', info.model_dump_json())


class ServerCommandInfoDataControl:
    def get_server_command_info(server_name: str) -> ServerCommandInfo:
        raw = __redis__.get(f'server_command_info:{server_name}')
        return ServerCommandInfo.model_validate_json(raw)

    def add_server_command_info(server_name: str, info: ServerCommandInfo):
        __redis__.set(f'server_command_info:{server_name}', info.model_dump_json())
        
    def remove_server_info(server_name: str):
        __redis__.delete(f'server_command_info:{server_name}')
        