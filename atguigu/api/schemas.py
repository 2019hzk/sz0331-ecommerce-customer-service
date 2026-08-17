"""
定义接口数据模型：和前端进行交互
继承BaseModel:在运行期间完成类型的校验和类型的转换
"""
from typing import Any

from pydantic import BaseModel


class ChatObject(BaseModel):
    id: str  # 商品编号 or  订单编号
    title: str  # 商品标题 or  订单标题
    type: str  # 点击的商品卡片 type:"product" 点击的是订单卡片 type:"order"
    attributes: dict[str, Any]  # 商品or订单的额外信息


class ChatBotMessage(BaseModel):
    text: str  # 机器人回复的内容（当下用的属性）
    object: ChatObject | None = None  # 后续扩展集成的属性


class ChatRequest(BaseModel):
    """
    聊天请求接口数据模型
    """
    sender_id: str
    text: str | None = None
    object: ChatObject | None = None


class ChatResponse(BaseModel):
    """
    聊天响应接口数据模型
    """
    message_id: str
    messages: list[ChatBotMessage]
