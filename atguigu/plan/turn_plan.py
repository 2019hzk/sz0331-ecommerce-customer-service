from dataclasses import dataclass
from typing import Any

from atguigu.task.commands.command import Command


@dataclass(slots=True)
class TaskTurnPlan:
    commands: list[Command]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskTurnPlan":
        return cls(
            commands=[Command.from_dict(command_dict) for command_dict in data['commands']]
        )


@dataclass(slots=True)
class KnowledgeTurnPlan:
    intents: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeTurnPlan":
        return cls(
            intents=[intent for intent in data['intents']]
        )


@dataclass(slots=True)
class ChitChatTurnPlan:
    chat: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ChitChatTurnPlan":
        return cls(
            chat=data['chat']
        )


@dataclass(slots=True)
class TurnPlan:
    task: TaskTurnPlan | None = None
    knowledge: KnowledgeTurnPlan | None = None
    chitchat: ChitChatTurnPlan | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TurnPlan":
        return cls(
            task=TaskTurnPlan.from_dict(data['task']) if data.get('task') is not None else None,
            knowledge=KnowledgeTurnPlan.from_dict(data['knowledge']) if data.get('knowledge') is not None else None,
            chitchat=ChitChatTurnPlan.from_dict(data['chitchat']) if data.get('chitchat') is not None else None
        )

