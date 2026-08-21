from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field

from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState



@dataclass(slots=True)
class ActionResult:
    messages:list[BotMessage]=field(default_factory=list)
    updated_slots:dict[str,Any]=field(default_factory=dict)





class Action(ABC):

    name: str

    @abstractmethod
    async def  run(self,action_kwargs:dict[str,Any],state:DialogueState)->ActionResult:
        pass






