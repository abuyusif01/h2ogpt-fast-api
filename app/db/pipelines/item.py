from typing import Any
from db.pipelines.utils.base_pipeline import BasePipeline
from schemas.response import APIExceptionResponse
from core.utils.exceptions import exhandler
from core.config import settings


class ItemPipeline(BasePipeline):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.db = settings.MONGO_ITEM_DB
        self.cursor = self.connection[self.db]

    @property
    @exhandler
    async def run(self) -> Any | APIExceptionResponse:
        return await self.items()

    async def items(self) -> list[dict]:
        query = [
            {"$project": {"_id": 0}},
        ]
        result = [result for result in self.cursor[self.db].aggregate(query)]

        return result

    async def insert_one(self, item: dict) -> dict:
        return self.cursor[self.db].insert_one(item)
