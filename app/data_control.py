import redis
from config import Config
from pydantic import ValidationError

from core.data_control.model.model import Model
from core.data_control.model.video_info import VideoInfo
from core.data_control.model.server_info import ServerInfo
from core.data_control.model.server_command_info import ServerCommandInfo
from core.data_control.model.server_power_status_info import ServerPowerStatusInfo
from core.singleton import Singleton

from loguru import logger

__redis__ = redis.Redis(host=Config.redis_host, port=Config.redis_port, password=Config.redis_pwd)

from typing import TypeVar, Generic, get_origin, get_args

T = TypeVar('T', bound=Model)

class RedisDataControl(Generic[T], metaclass=Singleton):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.__orig_bases__:
            orig_base = cls.__orig_bases__[0]
            if get_origin(orig_base) is RedisDataControl:
                cls.model_class = get_args(orig_base)[0]
                try:
                    if not issubclass(cls.model_class, Model): # if model_class is not subclass of Model, raise exception.
                        raise Exception('model_class should be subclass of Model', cls.model_class.__name__)
                    cls.model_class() # trying to make instanmc of model_class.
                except ValidationError as e:
                    pass
                except Exception as e:
                    logger.critical(f'Data controller can not accept the "{cls.model_class.__name__}" class as model_class. cause of ' + e.__str__())
                    pass

    def __init__(self) -> None:
       if self.model_class:
            print(self.model_class.get_name())

    def take_datas(self) -> set[T]:
        raw_sets = __redis__.smembers(self.model_class.get_name())
        datas = set[T]()
        for raw in raw_sets:
            datas.add(self.model_class.model_validate_json(raw))
        return datas

    def add(self, info: T):
        __redis__.sadd(self.model_class.get_name(), info.model_dump_json())
        
    def remove(self, info: T):
        __redis__.srem(self.model_class.get_name(), info.model_dump_json())

class VideoInfoDataControl(RedisDataControl[VideoInfo]): pass
class ServerInfoDataControl(RedisDataControl[ServerInfo]): pass

class ServerCommandInfoDataControl:
    def get_server_command_info(server_name: str) -> ServerCommandInfo:
        raw = __redis__.get(f'server_command_info:{server_name}')
        return ServerCommandInfo.model_validate_json(raw)

    def set_server_command_info(server_name: str, info: ServerCommandInfo):
        __redis__.set(f'server_command_info:{server_name}', info.model_dump_json())
        
    def remove_server_info(server_name: str):
        __redis__.delete(f'server_command_info:{server_name}')
        
class ServerPowerStatusInfoDataControl:
    def get_server_power_status_info(server_name: str) -> ServerPowerStatusInfo:
        raw = __redis__.get(f'server_power_status_info:{server_name}')
        return ServerPowerStatusInfo.model_validate_json(raw)

    def set_server_power_status_info(server_name: str, info: ServerPowerStatusInfo):
        __redis__.set(f'server_power_status_info:{server_name}', info.model_dump_json())
        
    def remove_server_info(server_name: str):
        __redis__.delete(f'server_power_status_info:{server_name}')
