import time

from atguigu.chitchat.handler import ChitChatHandler
from atguigu.clarify.responder import ClarifyResponder
from atguigu.domain.messages import ProcessedResult, BotMessage, UserMessage, MessageType
from atguigu.domain.state import DialogueState
from atguigu.knowledge.handler import KnowledgeHandler
from atguigu.plan.planner import TurnPlanner
from atguigu.plan.turn_plan import TurnPlan
from atguigu.plan.validator import TurnPlanValidator
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

        # 3.2 对象消息类型(TODO)
        else:
            bot_messages = await self._handle_object_message(dialogue_state)

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
        # # 3. 校验失败
        if not validated.valid:
            return await self.clarify_responder.respond(validated.reason, dialogue_state)

        # # 4. 校验成功(到底是哪一条轨道，进入到该轨道内部去执行对应的轨道内逻辑【xxxHandler】)
        # if turn_plan.task is not None:
        #     return self.task_handler.handle(turn_plan.task.commands)
        # elif turn_plan.knowledge is not None:
        #     return self.knowledge_handler.handle()
        # elif turn_plan.chitchat is not None:
        #     return self.chitchat_handler.handle()
        # else:
        #     pass

        # 5. 直接返回机器回复的消息
        return [BotMessage(text="你好，我是客服助手")]

    async def _handle_object_message(self, dialogue_state: DialogueState) -> list[BotMessage]:
        pass
