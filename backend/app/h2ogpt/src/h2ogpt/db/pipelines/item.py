import os
from typing import Any
from app.h2ogpt.src.h2ogpt.db.pipelines.utils.base_pipeline import BasePipeline
from app.h2ogpt.src.h2ogpt.schemas.response import APIExceptionResponse
from app.h2ogpt.src.h2ogpt.utils.exceptions import exhandler


class ItemPipeline(BasePipeline):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.db = os.getenv("MONGO_DB_H2OGPT_ITEMS") or "H2OGPT_ITEMS"

    @property
    @exhandler
    def run(self) -> Any | APIExceptionResponse:
        return self.items()

    def items(self) -> list[dict]:
        query = [
            {"$project": {"_id": 0}},
        ]
        result = [result for result in self.cursor[self.db].aggregate(query)]
        
        return result

    def insert_one(self, item: dict) -> dict:
        self.cursor[self.db].insert_one(item)
        return item
