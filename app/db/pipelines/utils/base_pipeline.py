from abc import ABC, abstractmethod
from db.pipelines.utils.cursor import Cursor


# TODO: Create a loggin module, and inherit it
class BasePipeline(Cursor, ABC):

    @abstractmethod
    async def run(self):
        raise NotImplementedError("Run method not implemented")
