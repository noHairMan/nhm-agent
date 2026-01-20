from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mercedes.core.registry import registry
from mercedes.utils.log import logger

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    agent_id: str = "default"


@router.post("/chat")
async def chat(request: ChatRequest):
    agent = registry.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")

    output = None
    async for output in agent.astream(request.message):
        logger.info(output)
    return output
