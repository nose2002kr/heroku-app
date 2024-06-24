from pydantic import BaseModel
from abc import abstractmethod, ABCMeta

class Model(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def __hash__(self):
        """
        This method is used to hash the object.
        """
        pass

    @abstractmethod
    def get_name():
        """
        This method is used to get the name of the object.
        The name is used to identify the object within Redis.
        """
        pass
    