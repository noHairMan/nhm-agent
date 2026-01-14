import asyncio
import os

import uvicorn


def get_unicorn_server():
    from mercedes.utils.conf import settings

    config = uvicorn.Config(
        "mercedes.app:app",
        host="0.0.0.0",
        port=4000,
        reload=True,
        log_config=settings.LOGGING,
    )
    server = uvicorn.Server(config)
    return server


async def main():
    os.environ.setdefault("MERCEDES_APP", "MERCEDES")
    os.environ.setdefault("MERCEDES_SETTINGS_MODULE", "mercedes.settings")

    server = get_unicorn_server()
    return await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
