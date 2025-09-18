import time
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TextIteratorStreamer,
)
from threading import Thread
from contextlib import asynccontextmanager

model_id = "qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    dtype=torch.float16,
    device_map="cpu",
    trust_remote_code=True
)
model = model.eval()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "Qwen2.5-0.5B"
    root: Optional[str] = None
    parent: Optional[str] = None
    permission: Optional[list] = None


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.2
    top_p: Optional[float] = 0.9
    max_length: Optional[int] = 512
    stream: Optional[bool] = False


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length"]


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]]


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))

@app.get("/v1/models", response_model=ModelList)
async def list_models():
    return ModelList(data=[ModelCard(id=model_id)])


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    global model, tokenizer

    if request.messages[-1].role != "user":
        raise HTTPException(status_code=400, detail="Invalid request(最后一条消息必须是user)")
    
    # 构造消息格式
    messages = []
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    # 转换为模型输入
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # 流式模式
    if request.stream:
        generate = predict(text, request)
        return EventSourceResponse(generate, media_type="text/event-stream")

    # 非流式模式
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            do_sample=True,
        )
    # 直接解码输出，确保只获取生成的部分，跳过输入提示
    response = tokenizer.decode(outputs[0][len(inputs.input_ids[0]):], skip_special_tokens=True)

    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role="assistant", content=response),
        finish_reason="stop"
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object="chat.completion")

async def predict(text: str, request: ChatCompletionRequest):
    global model, tokenizer
    
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=request.max_length,
        temperature=request.temperature,
        top_p=request.top_p,
        do_sample=True,
    )

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    # role 信息
    yield ChatCompletionResponse(
        model=request.model,
        object="chat.completion.chunk",
        choices=[ChatCompletionResponseStreamChoice(
            index=0,
            delta={"role": "assistant"},
            finish_reason=None
        )]
    ).json(exclude_unset=True, ensure_ascii=False)

    # 内容逐步输出
    response_content = ""
    for new_text in streamer:
        response_content += new_text
        yield ChatCompletionResponse(
            model=request.model,
            object="chat.completion.chunk",
            choices=[ChatCompletionResponseStreamChoice(
                index=0,
                delta={"content": new_text},
                finish_reason=None
            )]
        ).json(exclude_unset=True, ensure_ascii=False)

    # 结束
    yield ChatCompletionResponse(
        model=request.model,
        object="chat.completion.chunk",
        choices=[ChatCompletionResponseStreamChoice(
            index=0,
            delta={},
            finish_reason="stop"
        )]
    ).json(exclude_unset=True, ensure_ascii=False)
    yield "[DONE]"
    
def main():
    uvicorn.run(f"{__name__}:app", host='0.0.0.0', port=8000, workers=1)

if __name__ == '__main__':
    main()