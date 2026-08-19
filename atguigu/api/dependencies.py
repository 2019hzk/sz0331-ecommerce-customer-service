"""
管理service.
FASTAPI的依赖注入：Depends
Annotated；注解。可以将类型提示和依赖注入绑定在一起
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from atguigu.engines.dialogue_engine import DialogueEngine
from atguigu.repository.dialogue_repository import DialogueRepository
from atguigu.services.dialogue_service import DialogueStateService
from atguigu.infrastructure.db_client import session_factory  # 有坑  模块下的成员
from atguigu.infrastructure import  db_client                   # 包下面的模块 可以的
from  atguigu.engines.builder import  build_dialogue_engine

def get_dialogue_engine():
    return build_dialogue_engine()


DialogueEngineDep = Annotated[DialogueEngine, Depends(get_dialogue_engine)]


async def get_session():
    async with db_client.session_factory() as session:
        yield session  # 一定要yield出去，一旦return 代码块执行完，session对象又被释放掉了。用完，才来释放

DialogueSessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_dialogue_repository(session: DialogueSessionDep):
    return DialogueRepository(session)


DialogueRepositoryDep = Annotated[DialogueRepository, Depends(get_dialogue_repository)]


def get_dialogue_service(engine: DialogueEngineDep, repository: DialogueRepositoryDep):
    return DialogueStateService(engine, repository)


DialogueStateServiceDep = Annotated[DialogueStateService, Depends(get_dialogue_service)]
