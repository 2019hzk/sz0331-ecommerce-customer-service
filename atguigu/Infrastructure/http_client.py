"""

定义HTTP客户端(异步)

"""
import asyncio

from httpx import AsyncClient

http_client: AsyncClient | None = None


def init_http_client():
    """
    初始化http_client 资源
    """
    global http_client
    http_client = AsyncClient(timeout=120, trust_env=False)  # 参数作用：不用关心代理。


async def disposed_http_client():
    """
    释放http_client资源
    :return:
    """
    await http_client.aclose()


async def main_test():
    init_http_client()

    response = await http_client.get(url="http://192.168.200.155:18081/orders/A20260408002")

    print(response.json())
    data= response.json()['data']
    print(data)


if __name__ == '__main__':
    asyncio.run(main_test())
