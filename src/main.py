import asyncio

from langchain_ollama import ChatOllama

from mercedes.utils.conf import settings


def create_ollama_model(model: str = "gpt-oss:20b"):
    return ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        validate_model_on_init=True,
        temperature=0.8,
        num_predict=256,
    )


async def main():
    model = create_ollama_model()
    response = await model.ainvoke("你好，请自我介绍一下")
    print(f"\n回复: {response.content}")


if __name__ == "__main__":
    asyncio.run(main())
