"""

数据库的引擎
数据库连接工厂

"""
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy import text
from atguigu.config.settings import settings

session_engine: AsyncEngine | None = None

session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db_engine():
    global session_engine, session_factory

    session_engine = create_async_engine(url=settings.database_url, echo=True)  # echo=True 可以显示SQL语句
    session_factory = async_sessionmaker(session_engine, expire_on_commit=False)  # expire_on_commit


async def dispose_engine():
    await session_engine.dispose()


async def main_test():
    init_db_engine()

    async with session_factory() as session:
        cursor = await session.execute(text("select 1"))  # CursorResult
        print(cursor.mappings().fetchone())   # (1,)   # 元组：索引取元组中的元素    {'1': 1}: 字典：方便根据列名来获取


    await  dispose_engine()

if __name__ == '__main__':

    asyncio.run(main_test())
