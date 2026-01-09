from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """获取指定城市的实时天气信息。"""
    # 这里是一个 mock 实现
    return f"{city} 的天气是晴朗，25度。"


@tool
def get_datetime() -> str:
    """获取当前日期和时间。"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_default_tools():
    return [get_weather, get_datetime]
