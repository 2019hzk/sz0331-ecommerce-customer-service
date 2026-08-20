from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState


class  ChitChatHandler:
    async def handle(self,
                     chat:str,
                     dialogue_state:DialogueState)->list[BotMessage]:
        pass