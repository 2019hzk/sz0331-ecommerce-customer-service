import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert  # 注意mysql包

from atguigu.domain.state import DialogueState
from atguigu.repository.dialogue_record import DialogueRecord


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

        # 1. 定义SQL语句
        stmt = select(DialogueRecord).where(DialogueRecord.sender_id == sender_id)

        # 2. 执行SQL语句
        cursor_result = await self._session.execute(stmt)

        # 3. 获取结果对象
        dialogue_record = cursor_result.scalar_one_or_none()
        # 3.1 用户不存在
        if dialogue_record is None:
            return DialogueState(sender_id=sender_id)

        # 3.2 用户已经存在
        dialogue_record_dict = json.loads(dialogue_record.state_json)

        return DialogueState.from_dict(dialogue_record_dict)

    async def save_state(self,
                         sender_id: str,
                         dialogue_state: DialogueState):
        """
        职责：将引擎层修改后的对话状态保存到数据库中、
        如果用户之前不存在，调用save_state方法，像数据库中插入一条记录。
        如果用户之前存在， 调用save_state方法， 修改当前用户的state_json字段

        传统思路：插入记录之前，先根据sender_id查询，如果不存在在，保存 如果存在，修改
        SQL语句层面做：Insert or Update(唯一值：主键索引、唯一索引)
        MySQL:有插入和修改对应的升级SQL语句。

         INSERT INTO dialogue_states (sender_id, state_json) VALUES (%s, %s) AS new ON DUPLICATE KEY UPDATE state_json = new.state_json


        Args:
            sender_id:
            dialogue_state:

        Returns:

        """
        # 1.转换对话状态
        dialogue_state_dict = dialogue_state.to_dict()

        dialogue_state_str = json.dumps(dialogue_state_dict, ensure_ascii=False)

        # 2. 定义SQL语句
        # 2.1 定义INSERT的SQL语句
        insert_stmt = insert(DialogueRecord).values(sender_id=sender_id, state_json=dialogue_state_str)

        # 2.2 定义UPDATE的SQL语句
        update_stmt = insert_stmt.on_duplicate_key_update(state_json=insert_stmt.inserted.state_json)

        # 3. 执行SQL语句
        await self._session.execute(update_stmt)

        # 4. 手动提交
        await self._session.commit()
