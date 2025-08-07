from fastapi import FastAPI, Body
from pydantic import BaseModel
from app.model_loader import generate_text

app = FastAPI()

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
def chat(req: ChatRequest):
    """HTTP 接口：接收 prompt 并返回模型回复"""
    result = generate_text(req.prompt)
    return {"response": result}
