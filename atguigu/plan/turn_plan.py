from dataclasses import dataclass
from enum import Enum
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
            intents=data['intents']
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


    def  activated_tracks(self):
        activated_tracks:list[str]=[]

        if self.task is not None:
            activated_tracks.append("task")
        if self.knowledge is not None:
            activated_tracks.append("knowledge")
        if self.chitchat is not None:
            activated_tracks.append("chitchat")

        return  activated_tracks


class ClarifyReason(Enum):
    MISSING_TRACK = "missing_track"
    MULTIPLE_TRACKS = "multiple_tracks"
    MISSING_TASK_COMMANDS = "missing_task_commands"
    MISSING_KNOWLEDGE_INTENT = "missing_knowledge_intent"
    MISSING_FOCUSED_OBJECT = "missing_focused_object"
    OBJECT_REQUIRES_INTENT = "object_requires_intent"
    INVALID_TASK_COMMANDS = "invalid_task_commands"
    MULTIPLE_TASK_FLOWS = "multiple_task_flows"
    UNKNOWN_TASK_FLOW = "unknown_task_flow"



@dataclass(slots=True)
class TurnPlanValidatedResult:
    valid: bool
    reason: ClarifyReason | None=None

