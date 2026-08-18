from atguigu.domain.messages import UserMessage, ProcessedResult

from atguigu.engines.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository


class DialogueStateService:

    def __init__(self,
                engine: DialogueEngine,
                repository: DialogueRepository):
        self._engine = engine
        self._repository = repository

    async def process_message(self, user_message: UserMessage) -> ProcessedResult:
        """
        职责：处理对话消息的核心入口(service)
        Args:
            user_message:

        Returns:

        """
        # 1. 从数据库中读取当前用户的对话状态  I/O
        dialogue_state = await self._repository.load_state(user_message.sender_id)

        # 2. 引擎层使用（修改对话状态中的内容）计算
        processed_result = await  self._engine.handle_message(dialogue_state)

        # 3. 修改后的对话状态内容保存到数据库中 I/O
        await self._repository.save_state(user_message.sender_id, dialogue_state)

        return processed_result


