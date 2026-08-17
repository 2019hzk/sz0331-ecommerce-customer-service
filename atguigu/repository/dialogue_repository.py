from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.domain.state import DialogueState


class DialogueRepository:

    def __init__(self, session: AsyncSession):
        self._session = session


    async def load_state(self, sender_id: str) -> DialogueState:
        """
        职责：根据用户ID ,读取完整的对话状态
        Args:
            sender_id:

        Returns:

        """

    async def save_state(self,
                         sender_id: str,
                         dialogue_state: DialogueState):
        """
        职责：将引擎层修改后的对话状态保存到数据库中
        Args:
            sender_id:
            dialogue_state:

        Returns:

        """
