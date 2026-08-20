from atguigu.knowledge.intents import KnowledgeIntent


class KnowledgeHandler:
    def __init__(self, knowledge_intents: dict[str, KnowledgeIntent]):
        self.knowledge_intents = knowledge_intents

