from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from elroy.api import Elroy
from elroy.repository.memories.models import MemoryResponse

app = FastAPI(title="Elroy API", version="1.0.0", log_level="info")

# Style note: do not catch and reraise errors, outside of specific error handling, let regular errors propagate.


@app.get("/")
async def root():
    """Root endpoint that returns status ok."""
    return {"status": "ok"}


class MessageResponse(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    messages: List[MessageResponse]


class MemoryRequest(BaseModel):
    text: str


class ApiResponse(BaseModel):
    result: str


@app.get("/get_current_messages", response_model=List[MessageResponse])
async def get_current_messages():
    """Return a list of current messages in the conversation context."""
    elroy = Elroy()
    elroy.ctx

    messages = []
    for msg in elroy.get_current_messages():
        messages.append(MessageResponse(role=msg.role, content=msg.content or ""))

    return messages


@app.post("/create_augmented_memory", response_model=ApiResponse)
async def create_augmented_memory(request: MemoryRequest):
    elroy = Elroy()
    result = elroy.create_augmented_memory(request.text)
    return ApiResponse(result=result)


@app.get("/get_current_memories", response_model=List[MemoryResponse])
async def get_current_memories():
    """Return a list of memories for the current user."""
    elroy = Elroy()
    elroy.ctx

    memories = []
    for memory in elroy.get_current_memories():
        memories.append(MemoryResponse(title=memory.name, text=memory.text))

    return memories


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a user message and return the updated conversation."""
    elroy = Elroy()
    elroy.message(request.message)
    messages = []
    for msg in elroy.get_current_messages():
        if msg.content:
            messages.append(MessageResponse(role=msg.role, content=msg.content or ""))

    return ChatResponse(messages=messages)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
