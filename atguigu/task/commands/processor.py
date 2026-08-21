from atguigu.domain.contexts import SystemTaskCanceledContext, TaskContext, SystemTaskInterruptedContext, \
    SystemTaskStartedContext, SystemTaskResumeFailedContext, SystemTaskResumedContext
from atguigu.domain.state import DialogueState
from atguigu.task.commands.command import Command, StartFlowCommand, SetSlotsCommand, ResumedFlowCommand, \
    CancelFlowCommand
from atguigu.task.flows.flows import FlowList


class CommandProcessor:

    def process_command(self,
                        commands: list[Command],
                        state: DialogueState,
                        flow_list: FlowList):
        """
        职责：分别处理四种具体的命令
        Args:
            commands:
            dialogue_state:
            flow_list:

        Returns:

        """

        for command in commands:
            if isinstance(command, StartFlowCommand):
                self._start_flow(command, state, flow_list)
            elif isinstance(command, SetSlotsCommand):
                self._update_slots(command, state)
            elif isinstance(command, ResumedFlowCommand):
                self._resumed_flow(command, state, flow_list)
            elif isinstance(command, CancelFlowCommand):
                self._cancel_flow(state, flow_list)
            else:
                pass

    def _start_flow(self,
                    command: StartFlowCommand,
                    state: DialogueState,
                    flow_list: FlowList):
        """
        职责：业务目标：开启"业务"流程。代码逻辑（激活）更新业务流程上下文以及（激活）系统流程上下文
        Args:
            command:
            state:
            flow_list:

        Returns:

        """

        # 1. 获取当前要开启的业务流程ID
        start_flow_id = command.flow

        # 2. 获取当前要开启的业务流程名字
        start_flow_name = flow_list.get_flow_by_id(start_flow_id).name

        # 3. 获取当前正在执行业务流程上下文
        activate_task = state.active_task

        # 4. 当前正在执行的业务流程存在
        if activate_task is not None:
            # a) 当前正在执行业务流程的流程ID是等于要开启的业务流程的流程ID
            if activate_task.flow_id == start_flow_id:
                return  # 保持当前状态即可

            # b) 从挂起栈中移除要开启的业务流程的流程ID
            state.remove_paused_tasks(start_flow_id)

            interrupted_flow_id = activate_task.flow_id
            interrupted_flow_name = flow_list.get_flow_by_id(interrupted_flow_id).name
            # c) 中断当前业务正在执行的业务流程
            state.interrupt_active_task()

            # d) 激活业务流程以及中断系统流程
            state.start_task(TaskContext(
                flow_id=start_flow_id,
                step_id="start"
            ))

            state.start_system_task(SystemTaskInterruptedContext(
                flow_id="system_task_interrupted",
                step_id="start",
                interrupted_flow_id=interrupted_flow_id,
                interrupted_flow_name=interrupted_flow_name,
                started_flow_id=start_flow_id,
                started_flow_name=start_flow_name
            ))
        else:

            # a) 从挂起栈中移除要开启的业务流程的流程ID(有就移除，没有就不管)
            state.remove_paused_tasks(start_flow_id)

            # b) 激活业务流程
            state.start_task(TaskContext(
                flow_id=start_flow_id,
                step_id="start"
            ))

            # c) 激活开启系统流程
            state.start_system_task(SystemTaskStartedContext(
                flow_id="system_task_started",
                step_id="start",
                started_flow_id=start_flow_id,
                started_flow_name=start_flow_name
            ))

    def _update_slots(self,
                      command: SetSlotsCommand,
                      state: DialogueState):
        """
        职责：业务目标：给业务流程的缺失的槽位补全信息 代码逻辑：修改状态
        Args:
            command:
            state:

        Returns:

        """
        state.set_slots(command.slots)

    def _resumed_flow(self,
                      command: ResumedFlowCommand,
                      state: DialogueState,
                      flow_list: FlowList):
        """
        职责： 业务目标：恢复"业务"流程  代码逻辑（激活）更新业务流程上下文以及（激活）系统流程上下文
        Args:
            command:
            state:
            flow_list:

        Returns:

        """

        # 1. 获取要恢复的业务流程的流程ID(不一定有，如果在恢复的时候没有明确的恢复目标，那么flow是None)
        resumed_flow_id = command.flow

        # 2. 获取当前正在执行的业务流程上下文
        activate_task = state.active_task

        # 3. 当前正在执行的业务流程存在
        if activate_task is not None:

            # 3.1 判断要恢复的业务流程的流程ID是否为空
            if resumed_flow_id is None:
                return  # 保持当前状态

            # 3.2 判断是否和当前正在执行的业务流程一样
            if resumed_flow_id == activate_task.flow_id:
                return  # 保持当前状态

            interrupted_flow_id = activate_task.flow_id
            interrupted_flow_name = flow_list.get_flow_by_id(interrupted_flow_id).name

            # 3.3 中断当前正在执行的业务流程
            state.interrupt_active_task()

            # 3.4 从挂起业务流程上下文的栈中恢复
            resumed = state.resume_task(resumed_flow_id)

            # 3.5 没有恢复成功
            if not resumed:
                # a) 回滚 把刚刚压入到栈中的当前执行的业务流程上下文恢复出来
                state.resume_task()

                # b) 激活恢复失败的系统流程
                state.start_system_task(SystemTaskResumeFailedContext(
                    flow_id="system_task_resume_failed",
                    step_id="start"
                ))
            else:
                # c) 激活中断系统流程
                state.start_system_task(SystemTaskInterruptedContext(
                    flow_id="system_task_interrupted",
                    step_id="start",
                    interrupted_flow_id=interrupted_flow_id,
                    interrupted_flow_name=interrupted_flow_name,
                    started_flow_id=state.active_task.flow_id,
                    started_flow_name=flow_list.get_flow_by_id(state.active_task.flow_id).name
                ))

        else:
            resumed = state.resume_task(resumed_flow_id)
            if not resumed:
                # a) 激活恢复失败的系统流程
                state.start_system_task(SystemTaskResumeFailedContext(
                    flow_id="system_task_resume_failed",
                    step_id="start"
                ))
            else:
                # b) 激活恢复成功系统流程
                state.start_system_task(SystemTaskResumedContext(
                    flow_id="system_task_resumed",
                    step_id="start",
                    resumed_flow_id=state.active_task.flow_id,
                    resumed_flow_name=flow_list.get_flow_by_id(state.active_task.flow_id).name
                ))

    def _cancel_flow(self,
                     state: DialogueState,
                     flow_list: FlowList):
        """
        职责： 业务目标：取消"业务"流程  代码逻辑（激活）更新业务流程上下文以及（激活）系统流程上下文
        Args:
            state:
            flow_list:

        Returns:

        """

        # 1. 获取当前系统中正在执行的业务流程
        activated_task = state.active_task

        # 2. 取消业务流程以及系统流程
        state.cancel_active_task()

        # 3. 激活取消系统流程(让用户看到取消系统流程的开场白)
        state.start_system_task(SystemTaskCanceledContext(
            flow_id="system_task_canceled",
            step_id="start",
            canceled_flow_id=activated_task.flow_id,
            canceled_flow_name=flow_list.get_flow_by_id(activated_task.flow_id).name
        ))
