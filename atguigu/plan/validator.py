from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import TurnPlan, TurnPlanValidatedResult, ClarifyReason, TaskTurnPlan, KnowledgeTurnPlan
from atguigu.task.flows.flows import FlowList
from atguigu.task.commands.command import StartFlowCommand, SetSlotsCommand, CancelFlowCommand, ResumedFlowCommand


class TurnPlanValidator:
    def valid(self,
              turn_plan: TurnPlan,
              dialogue_state: DialogueState,
              *,
              flow_list: FlowList,
              knowledge_intents: dict[str, KnowledgeIntent]
              ) -> TurnPlanValidatedResult:
        """
        职责：对轮次规划后的结果校验
        1.校验轨道数（命中了几条轨道：外部校验）
        2.校验轨道内部（进入到轨道内部校验）
        Args:
            turn_plan:
            dialogue_state:

        Returns:

        """

        # 1. 获取路由后的轨道情况
        activated_tracks = turn_plan.activated_tracks()

        # 2. 是否未命中轨道
        if not activated_tracks:
            return self._reject(ClarifyReason.MISSING_TRACK)

        # 3. 是否命中多条轨道
        if len(activated_tracks) > 1:
            return self._reject(ClarifyReason.MULTIPLE_TRACKS)

        # 4. 命中唯一的轨道
        selected_tracks = activated_tracks[0]

        # 4.1 进入到task轨道校验
        if selected_tracks == "task":
            return self._validate_task_track(turn_plan.task, flow_list)

        # 4.2 进入到knowledge轨道校验
        if selected_tracks == "knowledge":
            return self._validate_knowledge_track(turn_plan.knowledge, dialogue_state, knowledge_intents)

        # 4.3 闲聊轨道不校验(不校验)
        return TurnPlanValidatedResult(valid=True)

    def _reject(self, reason: ClarifyReason) -> TurnPlanValidatedResult:
        return TurnPlanValidatedResult(valid=False, reason=reason)

    def _validate_task_track(self,
                             task: TaskTurnPlan,
                             flow_list: FlowList) -> TurnPlanValidatedResult:
        """
        职责：校验task轨道
        校验1：task轨道是否有对应的命令（commands）
        校验2：命令(command)是否合法
        校验3: 是否有多个开启command
        校验4：是否有流程
        TODO: 更多的校验规则
        Args:
            task:
            dialogue_state:
            flow_list:

        Returns:

        """

        # 1. task轨道是否有对应的命令（commands）
        if not task.commands:
            return self._reject(ClarifyReason.MISSING_TASK_COMMANDS)

        # 2. 命令(command)是否合法(简单判断)
        allowed_commands = (StartFlowCommand, SetSlotsCommand, CancelFlowCommand, ResumedFlowCommand)
        if not all(isinstance(command, allowed_commands) for command in task.commands):
            return self._reject(ClarifyReason.INVALID_TASK_COMMANDS)

        # 3. 是否有多个开启command（校验）
        start_command = [command for command in task.commands if isinstance(command, StartFlowCommand)]
        if len(start_command) > 1:
            return self._reject(ClarifyReason.MULTIPLE_TASK_FLOWS)

        if start_command:
            flow_id = start_command[0].flow
            flow = flow_list.get_flow_by_id(flow_id)
            if flow is None:
                return self._reject(ClarifyReason.UNKNOWN_TASK_FLOW)

        # 4. 通过(给业务流程设置槽位命令、取消业务流程命令、恢复业务流程命令)
        return TurnPlanValidatedResult(valid=True)

    def _validate_knowledge_track(self,
                                  knowledge: KnowledgeTurnPlan,
                                  dialogue_state: DialogueState,
                                  knowledge_intents: dict[str, KnowledgeIntent]) -> TurnPlanValidatedResult:

        """
        职责：校验knowledge轨道
        校验:接口提供者【api.order/api.product】意图对象是否填写对应的卡片对象
        对象的源头约束：只能点击页面标签获取，不支持从输入框中根据用户的自然语言提取对象出来。【llm分析 提取】
        Args:
            knowledge:
            dialogue_state:
            knowledge_intents:

        Returns:

        """

        # 1. 是否分析出来知识意图
        if not knowledge.intents:
            return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)

        for llm_intent in knowledge.intents:
            knowledge_object = knowledge_intents[llm_intent]
            require_type = knowledge_object.requires_object_type

            focused_object = dialogue_state.focused_object
            if require_type is not None:
                if  focused_object is None or focused_object.type!= require_type:
                    return self._reject(ClarifyReason.MISSING_FOCUSED_OBJECT)


        return    TurnPlanValidatedResult(valid=True)


