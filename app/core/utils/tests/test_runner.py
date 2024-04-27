from schemas.response import APIExceptionResponse
from core.utils.runner import PipelineNames, PipelineRunner


class Test_Runner:
    def test_pipeline(self):
        pipeline = "ITEM"
        res = PipelineRunner(
            pipeline_name=PipelineNames[pipeline],
            chatId="7477ef00-d4e8-477a-9322-867c40a68286",
        ).run()

        assert isinstance(res, list)
        assert len(res) > 0
        assert not isinstance(res, APIExceptionResponse), "Exception something failed"
