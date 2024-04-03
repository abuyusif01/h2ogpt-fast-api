from abc import ABC, abstractmethod
from app.h2ogpt.src.h2ogpt.db.pipelines.utils.cursor import Cursor


# TODO: Create a loggin module, and inherit it
class BasePipeline(Cursor, ABC):

    @abstractmethod
    def run(self):
        raise NotImplementedError("Not Implemented")
