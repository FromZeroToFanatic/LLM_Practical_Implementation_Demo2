from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import torch
import uvicorn
import json
import asyncio

pretrained = "qwen/Qwen2.5-0.5B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(pretrained, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    pretrained,
    dtype=torch.float16,
    device_map="cpu",
    trust_remote_code=True
)
model = model.eval()

# 创建 FastAPI 应用
app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载测试用的 HTML 前端页面
with open("websocket.html") as f:
    html = f.read()

@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 接口说明：
    - 输入: JSON 格式 {"query": "", "history": []}
    - 输出: JSON 格式 {"response": "", "history": [], "status": 200}
    其中 status=202 表示响应正在生成，status=200 表示生成结束
    """
    await websocket.accept()
    try:
        while True:
            # 1. 接收客户端发来的 query + history
            json_request = await websocket.receive_json()
            query = json_request['query']
            history = json_request.get('history', [])

            # 2. 构造 messages 格式（Qwen 需要）
            messages = [{"role": "system", "content": "你是一个友好的 AI 助手。"}]
            for h in history:
                messages.append({"role": "user", "content": h[0]})
                messages.append({"role": "assistant", "content": h[1]})
            messages.append({"role": "user", "content": query})

            # 3. 转换为模型输入
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            inputs = tokenizer(text, return_tensors="pt").to(model.device)

            # 4. 实现真正的流式输出
            # 使用 TextIteratorStreamer 进行流式处理
            streamer = TextIteratorStreamer(
                tokenizer,
                skip_prompt=True,
                skip_special_tokens=True,
                timeout=10.0
            )

            # 5. 定义生成函数
            def generate():
                with torch.no_grad():
                    model.generate(
                        **inputs,
                        streamer=streamer,
                        max_new_tokens=512,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=False,
                        pad_token_id=tokenizer.eos_token_id
                    )

            # 6. 在单独线程中运行模型生成
            import threading
            thread = threading.Thread(target=generate)
            thread.start()

            # 7. 异步流式发送结果
            collected_tokens = []
            for token in streamer:
                collected_tokens.append(token)
                full_response = ''.join(collected_tokens)
                # 发送中间结果，status=202表示生成中
                await websocket.send_json({
                    "response": full_response,
                    "history": history + [[query, full_response]],
                    "status": 202
                })

            # 8. 等待线程结束
            thread.join()

            # 9. 最终结果，status=200表示完成
            final_response = ''.join(collected_tokens)
            history.append([query, final_response])
            
            # 10. 发送最终结果
            await websocket.send_json({
                "response": final_response,
                "history": history,
                "status": 200
            })

    except WebSocketDisconnect:
        pass

def main():
    uvicorn.run(f"{__name__}:app", host='0.0.0.0', port=8000, workers=1)


if __name__ == '__main__':
    main()