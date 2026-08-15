"""
消息的类型有几种：
1. 用户角色的消息
2. 机器人角色回复的消息


不管是进行网络传输或者是进行IO读写：永远都不能直接操作"对象" 对象是内存中的。



"""
from enum import Enum
from typing import Any
from dataclasses import dataclass


class MessageType(Enum):
    TEXT = "text"
    OBJECT = "object"


@dataclass(slots=True)  # 内存占用空间少 访问速度快 对象的属性个数是固定的
class FocusedObject:
    """
    消息类型是对象
    """
    id: str  # 商品编号 or  订单编号
    title: str  # 商品标题 or  订单标题
    type: str  # 点击的商品卡片 type:"product" 点击的是订单卡片 type:"order"
    attributes: dict[str, Any]  # 商品or订单的额外信息

    def to_dict(self) -> dict[str, Any]:
        """
        将self的实例对象转换为字典对象：
        对象：业务代码使用的
        字典---json格式字符串--->数据库写操作的时候使用的
        :return:
        """

        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "attributes": self.attributes
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FocusedObject":
        """
        将字典对象转成实例对象
        :param data:
        :return:
        """
        return cls(
            id=data['id'],
            title=data['title'],
            type=data['type'],
            attributes=data['attributes']
        )


@dataclass(slots=True)
class UserMessage:
    """
    用户角色消息的领域数据模型（业务代码直接操作的：不包括api路由层）
    """
    sender_id: str  # 用户ID:前端会带过来
    message_id: str  # 消息ID:自己生成
    type: MessageType  # 消息类型：文本消息类型以及对象消息类型【枚举】
    text: str | None = None  # 文本类型消息的内容
    object: FocusedObject | None = None  # 对象类型消息的内容

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "type": self.type.value,
            "text": self.text,
            "object": FocusedObject.to_dict(self.object) if self.object is not None else None
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserMessage":
        return cls(
            sender_id=data['sender_id'],
            message_id=data['message_id'],
            type=MessageType(data['type']),
            text=data['text'],
            object=FocusedObject.from_dict(data['object']) if data['object'] is not None else None
        )


@dataclass(slots=True)
class BotMessage:
    text: str  # 机器人回复的内容（当下用的属性）
    object: FocusedObject | None = None  # 后续扩展集成的属性


    def  to_dict(self)->dict[str,Any]:
        return {
            "text": self.text,
            "object": FocusedObject.to_dict(self.object) if self.object is not None else None
        }
    @classmethod
    def  from_dict(cls,data:dict[str,Any])->"BotMessage":
        return  cls(
            text=data['text'],
            object=FocusedObject.from_dict(data['object']) if data['object'] is not None else None
        )
