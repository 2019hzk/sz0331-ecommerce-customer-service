from atguigu.domain.messages import ProcessedResult
from atguigu.domain.state import DialogueState


class DialogueEngine:
    async def handle_message(self, dialogue_state: DialogueState) -> ProcessedResult:
        """"
        TODO:明天做（调用LLM 做路由分析、校验分析后的结果、进入到对应轨道内部处理、推进流程..）
        """
