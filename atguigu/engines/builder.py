from pathlib import Path

from atguigu.chitchat.handler import ChitChatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.engines.dialogue_engine import DialogueEngine
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.validator import TurnPlanValidator
from atguigu.task.flows.loader import FlowLoader
from atguigu.task.handler import TaskHandler

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[2]

FLOW_CONFIG_DIR = PROJECT_ROOT_DIR / "flow_config"


def build_dialogue_engine():
    # 1. 加载流程
    flow_list = FlowLoader().load_multi_yaml(
        [FLOW_CONFIG_DIR / yaml for yaml in ("system_flows.yml", "user_flows.yml")])

    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_plan_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponder(),
        task_handler=TaskHandler(
            flow_list=flow_list
        ),
        knowledge_handler=KnowledgeHandler(knowledge_intents=KNOWLEDGE_INTENTS),
        chitchat_handler=ChitChatHandler()
    )
