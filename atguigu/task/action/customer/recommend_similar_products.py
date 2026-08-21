from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class ActionRecommendSimilarProducts(Action):
    name = "action_recommend_similar_products"

    async def run(self, action_kwargs: dict[str, Any], state: DialogueState) -> ActionResult:
        """
        TODO  (暂时中台服务未提供相似商品推荐功能)
        Args:
            action_kwargs:
            state:

        Returns:

        """

        return  ActionResult()


