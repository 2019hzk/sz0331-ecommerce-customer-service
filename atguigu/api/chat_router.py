"""
定义路由
"""
import uuid
from dataclasses import dataclass
from fastapi import APIRouter, Depends

from atguigu.api.schemas import ChatResponse, ChatRequest, ChatBotMessage, ChatObject
from atguigu.domain.messages import UserMessage, ProcessedResult, MessageType, FocusedObject
from atguigu.api.dependencies import DialogueStateServiceDep

router = APIRouter()


@router.get("/")
def hello_endpoint():
    """
    接口响应层：FASTAPI自动会将接口返回的对象序列化为json格式字符串:序列化
    接口请求处理层： FASTAPI自动的将前端发送的json格式字符串反序列化成数据模型对象【数据模型出来】：反序列化

    Returns:

    """

    return {"success": "ok"}


@dataclass(slots=True)
class User:
    name: str
    age: int
    address: str


@router.get("/test", response_model=User)
def test_endpoint():
    """
    response_model:
    作用1：校验器作用
    作用2：过滤器作用
    作用3：生成丰富的接口文档信息（作用）
    Returns:

    """
    return {
        "name": "zs",
        "age": "18",
        "address": "sz",
        "card_no": "xxxxxxxabcdddddddd"
    }


@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest,
                        service: DialogueStateServiceDep):
    # 1.将接口数据模型转成领域数据模型
    user_message = _build_user_message(chat_request)

    # 2.调用service处理领域数据模型---返回的还是领域数据模型
    processed_result = await service.process_message(user_message)

    # 3. 将处理后的领域数据 模型转成接口数据模型
    chat_response = _build_chat_response(processed_result)

    return chat_response


def _build_user_message(chat_request: ChatRequest) -> UserMessage:
    """
    职责：接口数据模型转成领域数据模型
    Args:
        chat_request:

    Returns:

    """

    return UserMessage(
        sender_id=chat_request.sender_id,
        message_id=str(uuid.uuid4().hex),
        type=MessageType.OBJECT if chat_request.object is not None else MessageType.TEXT,
        text=chat_request.text,
        object=FocusedObject(
            id=chat_request.object.id,
            type=chat_request.object.type,
            title=chat_request.object.title,
            attributes=chat_request.object.attributes,
        ) if chat_request.object is not None else None
    )


def _build_chat_response(processed_result: ProcessedResult) -> ChatResponse:
    """
     职责：处理后的领域数据模型转成接口数据模型
    Args:
        processed_result:

    Returns:

    """

    return ChatResponse(
        message_id=processed_result.message_id,
        messages=[
            ChatBotMessage(
                text=bot_message.text,
                object=ChatObject(
                    id=bot_message.object.id,
                    type=bot_message.object.type,
                    title=bot_message.object.title,
                    attributes=bot_message.object.attributes
                ) if bot_message.object is not None else None
            )
            for bot_message in processed_result.messages
        ]
    )
