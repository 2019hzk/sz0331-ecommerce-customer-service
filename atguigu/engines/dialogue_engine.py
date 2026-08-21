import time

from atguigu.chitchat.handler import ChitChatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.domain.messages import ProcessedResult, BotMessage, UserMessage, MessageType, FocusedObject
from atguigu.domain.state import DialogueState
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_plan import TurnPlan, ClarifyReason
from atguigu.plan.validator import TurnPlanValidator
from atguigu.task.commands.command import Command, SetSlotsCommand
from atguigu.task.flows.flows import FlowList
from atguigu.task.flows.steps import CollectionFlowStep
from atguigu.task.handler import TaskHandler


class DialogueEngine:

    def __init__(self,
                 turn_planner: TurnPlanner,
                 turn_plan_validator: TurnPlanValidator,
                 clarify_responder: ClarifyResponder,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowledgeHandler,
                 chitchat_handler: ChitChatHandler
                 ):
        self.turn_planner = turn_planner
        self.turn_plan_validator = turn_plan_validator
        self.clarify_responder = clarify_responder
        self.task_handler = task_handler
        self.knowledge_handler = knowledge_handler
        self.chitchat_handler = chitchat_handler

    async def handle_message(self,
                             user_message: UserMessage,
                             dialogue_state: DialogueState) -> ProcessedResult:
        """
        职责：处理消息的核心入口
        Args:
            user_message:
            dialogue_state:

        Returns:

        """

        # 1. 准备session
        self._prepare_session(dialogue_state)

        # 2. 开启turn
        self._start_turn(user_message, dialogue_state)

        # 3. 消息分流（文本消息 or 对象消息）
        # 3.1 文本消息类型
        if user_message.type is MessageType.TEXT:
            bot_messages = await self._handle_text_message(dialogue_state)

        # 3.2 对象消息类型
        else:
            # a) 将点击的卡片存储到对话状态中
            dialogue_state.focused_object = user_message.object

            # b) 真正处理对象消息
            bot_messages = await self._handle_object_message(user_message.object, dialogue_state,
                                                             self.task_handler.flow_list)

        # 4. 提交
        dialogue_state.pending_turn.bot_messages = bot_messages
        dialogue_state.commit_pending_turn()

        # 5. 返回机器人回复的消息
        return ProcessedResult(message_id=user_message.message_id, messages=bot_messages)

    def _prepare_session(self,
                         state: DialogueState):
        """
        职责：创建session对象
        Args:
            dialogue_state:

        Returns:

        """

        # 1. 获取当前session
        current_session = state.current_session()

        # 2. 当前session没有
        if current_session is None:
            # a) 创建session
            state.start_session()
        # 3. 当前session有
        else:
            # 3.1 判断session是否过期了（简单规则）
            now = time.time()
            # 过期了
            if now - current_session.activated_at > 60 * 60:
                # a) 关闭过期的session
                state.close_current_session()

                # b) 重置运行时该过期session的对话状态
                state.reset_runtime_state_for_new_session()

                # c) 创建新session出来
                state.start_session()
            # 没过期
            else:
                current_session.activated_at = now

    def _start_turn(self,
                    user_message: UserMessage,
                    state: DialogueState):

        state.begin_turn(user_message)

    async def _handle_text_message(self, dialogue_state: DialogueState) -> list[BotMessage]:
        """
        职责：处理文本消息类型（llm进行路由分析，规划轨道）
        Args:
            dialogue_state:
        Returns:
        """
        # 1. 利用轮次规划器进行路由分析
        turn_plan: TurnPlan = await self.turn_planner.predict(dialogue_state,
                                                              flow_list=self.task_handler.flow_list,
                                                              knowledge_intents=self.knowledge_handler.knowledge_intents)

        # 2. 利用轮次结果校验器校验轮次规划后的结果
        validated = self.turn_plan_validator.valid(turn_plan,
                                                   dialogue_state,
                                                   flow_list=self.task_handler.flow_list,
                                                   knowledge_intents=self.knowledge_handler.knowledge_intents
                                                   )
        #  3. 校验失败
        if not validated.valid:
            return await self.clarify_responder.respond(validated.reason, dialogue_state)

        # 4. 校验成功(到底是哪一条轨道，进入到该轨道内部去执行对应的轨道内逻辑【xxxHandler】)
        if turn_plan.task is not None:
            return await self.task_handler.handle(turn_plan.task.commands, dialogue_state)
        elif turn_plan.knowledge is not None:
            return await self.knowledge_handler.handle(turn_plan.knowledge.intents, dialogue_state)
        else:
            return await self.chitchat_handler.handle(turn_plan.chitchat.chat, dialogue_state)

    async def _handle_object_message(self,
                                     object: FocusedObject,
                                     dialogue_state: DialogueState,
                                     flow_list: FlowList) -> list[BotMessage]:
        """
        职责：处理对象类型，本质构建SetSlotsCommand对象
        Args:
            dialogue_state:

        Returns:

        """

        # 1. 尝试构建SetSlotsCommand对象
        command = self._try_build_set_slots_command(object, dialogue_state, flow_list)

        # 2. 判断command  # 情况3：流程继续推进下一步
        if command:
            return await self.task_handler.handle(commands=[command], dialogue_state=dialogue_state)

        if dialogue_state.active_task is not None:  # 情况2: 流程继续执行，但是不去推进下一步，而是在执行当前这一步
            return await self.task_handler.handle(commands=[], dialogue_state=dialogue_state)

        # 情况1:澄清
        return await self.clarify_responder.respond(reason=ClarifyReason.OBJECT_REQUIRES_INTENT,
                                                    dialogue_state=dialogue_state)

    def _try_build_set_slots_command(self,
                                     object: FocusedObject,
                                     dialogue_state: DialogueState,
                                     flow_list: FlowList) -> Command | None:
        """
        职责：两种卡片类型的槽位（订单类型的槽位 商品信息的槽位）
        Args:
            dialogue_state:
            flow_list:

        Returns:

        """
        if object.type == "order":
            if self._is_can_set_slots_command(slot_name="order_number", state=dialogue_state, flow_list=flow_list):
                return SetSlotsCommand(command="set_slots", slots={"order_number": object.id})
            return None
        elif object.type == "product":
            if self._is_can_set_slots_command(slot_name="product_id", state=dialogue_state, flow_list=flow_list):
                return SetSlotsCommand(command="set_slots", slots={"product_id": object.id})
            return None
        else:
            return None

    def _is_can_set_slots_command(self,
                                  slot_name: str,
                                  state: DialogueState,
                                  flow_list: FlowList) -> bool:
        """
        职责：处理点击卡片的三种情况
        情况1：没有业务流程，返回False
        情况2：有业务流程，但是收集步骤的时候，并不缺少卡片信息，返回False
        情况3：有业务流程，刚好收集该步骤的时候，点击卡片信息，返回True
        Args:
            slot_name:
            state:
            flow_list:

        Returns:

        """

        # 1. 获取当前业务流程上下文
        task_context = state.active_task

        # 2. 判读当前业务流程上下文,不存在
        if task_context is None:
            return False

        # 3.判读当前业务流程上下文,存在
        flow = flow_list.get_flow_by_id(task_context.flow_id)
        if flow is None:  # 防御性代码
            return False

        # 4. 判断流程步骤是否存在
        step_id = task_context.step_id
        step = flow.get_step_by_id(step_id)
        if step is None:  # 防御性代码
            return False

        # 5. 获取当前步骤类型
        if not isinstance(step, CollectionFlowStep):
            return False

        return step.slot_name == slot_name
