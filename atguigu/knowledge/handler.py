from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent


class KnowledgeHandler:
    def __init__(self, knowledge_intents: dict[str, KnowledgeIntent]):
        self.knowledge_intents = knowledge_intents

    async def handle(self,
                     intents:list[str],
                     dialogue_state:DialogueState)->list[BotMessage]:
        pass

