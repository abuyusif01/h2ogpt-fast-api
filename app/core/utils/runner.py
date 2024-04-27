from enum import Enum
from db.pipelines.chat import ChatPipeline
from db.pipelines.item import ItemPipeline


class PipelineNames(Enum):
    CHAT = "ChatPipeline"
    ITEM = "ItemPipeline"


class PipelineRunner:
    pipelines = {
        PipelineNames.CHAT: ChatPipeline,
        PipelineNames.ITEM: ItemPipeline,
    }

    def __init__(self, pipeline_name: PipelineNames, **kwargs) -> None:
        if pipeline_name in self.pipelines:
            self.pipeline = self.pipelines[pipeline_name](**kwargs)
        else:
            raise ValueError(f"Invalid pipeline name: {pipeline_name}")
    
    async def run(self):
        return await self.pipeline.run
