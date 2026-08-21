from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult



class ActionLookupLogisticsStatus(Action):
    name = "action_lookup_logistics"

    async def run(self, action_kwargs: dict[str, Any], state: DialogueState) -> ActionResult:
        """
        TODO
        Args:
            action_kwargs:
            state:

        Returns:

        """

        # 1. 获取请求参数
        order_number=state.active_task.slots.get('order_number')

        # 2. 给中台服务发送获取订单物流的请求

        # 3. 封装到ActionResult的slots中返回

        return  ActionResult()




