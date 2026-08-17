from sqlalchemy.orm import Mapped,mapped_column
from  atguigu.repository.base import  Base
from sqlalchemy import  TEXT

class DialogueRecord(Base):
    __tablename__ = "dialogue_states"

    sender_id:Mapped[str]=mapped_column(primary_key=True)        # Mapped:可以在ide中进行类型提示和自动补全，类型推断：自动推断数据库对应列的类型
    state_json:Mapped[str]=mapped_column(TEXT,nullable=False,default="{}")



