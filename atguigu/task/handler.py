from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.commands.command import Command
from atguigu.task.flows.flows import FlowList


class TaskHandler:

    def __init__(self, flow_list: FlowList):
        self.flow_list = flow_list

    async def handle(self,
               commands: list[Command],
               dialogue_state:DialogueState)->list[BotMessage]:
        return [BotMessage(text="你好，我是智能客服")]
