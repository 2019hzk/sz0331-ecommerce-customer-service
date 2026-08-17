from atguigu.domain.contexts import TaskContext
from atguigu.domain.messages import ProcessedResult, BotMessage
from atguigu.domain.state import DialogueState


class DialogueEngine:
    async def handle_message(self, dialogue_state: DialogueState) -> ProcessedResult:
        """"
        TODO:明天做（调用LLM 做路由分析、校验分析后的结果、进入到对应轨道内部处理、推进流程..）
        """

        dialogue_state.active_task=TaskContext(flow_id="order_status_query",step_id="start")

        return ProcessedResult(message_id="1234",messages=[BotMessage(text="我是智能小助手")])
