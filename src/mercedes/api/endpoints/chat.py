from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mercedes.core.registry import registry

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    agent_id: str = "default"


@router.post("/chat")
async def chat(request: ChatRequest):
    agent = registry.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")

    reply = await agent.run(request.message)
    return {"reply": reply, "agent_id": request.agent_id}
