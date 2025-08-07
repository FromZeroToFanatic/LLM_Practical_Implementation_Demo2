import asyncio
import websockets
import json
from app.model_loader import tokenizer, model, streamer
import torch

# WebSocket 服务端处理函数
async def echo(websocket):
    async for message in websocket:
        try:
            data = json.loads(message)
            prompt = data.get("prompt", "")
            inputs = tokenizer(prompt, return_tensors="pt")
            # 模型生成时将结果通过流式输出发送给客户端
            generate_kwargs = dict(inputs, streamer=streamer, max_new_tokens=512)
            model.generate(**generate_kwargs)
            await websocket.send("[END]")
        except Exception as e:
            await websocket.send(f"[ERROR] {str(e)}")

# 启动 WebSocket 服务
async def main():
    async with websockets.serve(echo, "localhost", 8765):
        print("✅ WebSocket 服务启动：ws://localhost:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
