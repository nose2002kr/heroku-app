import redis
from config import Config
from pydantic import ValidationError

from core.data_control.model import Model
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
       self.key = self.model_class.get_name()

    def __get_name(self, name: str) -> str:
        return self.key + ':' + name

    def take_all(self) -> list[T]:
        names = self.get_names()
        datas = list[T]()
        for name in names:
            data = self.take(name)
            if data is None:
                logger.debug('data is None for ' + name)
                continue
            datas.append(data)
        return datas

    def take(self, name: str) -> T | None:
        raw = __redis__.get(self.__get_name(name))
        if raw is None:
            logger.debug('raw is None for ' + self.__get_name(name))
            return None
        return self.model_class.model_validate_json(raw)

    def get_names(self) -> list[str]:
        raw_sets = __redis__.zrange(self.key, 0, -1)
        datas = list[str]()
        for raw in raw_sets:
            datas.append(raw.decode('utf-8'))
        return datas

    def add(self, name: str, info: T):
        max = __redis__.zrevrange(self.key, 0, -1, withscores=True)
        if len(max) == 0: max = 0
        else            : max = max[0][1]
        logger.debug('calcuated highest number ' + str(max))
        
        key_name = self.__get_name(name)
        __redis__.zadd(self.key, {name: max + 1}, nx=True)
        __redis__.set(key_name, info.model_dump_json())
        logger.debug(f'set to ({max}): {key_name}')
    
    def set(self, name: str, info: T):
        key_name = self.__get_name(name)
        
        if not __redis__.exists(key_name):
            logger.debug(f'the "{key_name}" not exists, add.')
            self.add(name, info)
        else:
            __redis__.set(key_name, info.model_dump_json())

    def remove(self, name: str):
        __redis__.zrem(self.key, name)
        __redis__.delete(self.__get_name(name))
        

class VideoInfoDataControl(RedisDataControl[VideoInfo]): pass
class ServerInfoDataControl(RedisDataControl[ServerInfo]): pass
class ServerCommandInfoDataControl(RedisDataControl[ServerCommandInfo]): pass
class ServerPowerStatusInfoDataControl(RedisDataControl[ServerPowerStatusInfo]): pass
