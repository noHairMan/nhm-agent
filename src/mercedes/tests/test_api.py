import asyncio

import httpx


async def test_chat():
    url = "http://127.0.0.1:8000/api/chat"
    payload = {"message": "北京现在的天气怎么样？", "agent_id": "default"}

    print(f"发送请求: {payload}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30.0)
            print(f"状态码: {response.status_code}")
            print(f"回复内容: {response.json()}")
    except Exception as e:
        print(f"请求失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_chat())
