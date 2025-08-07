import asyncio
import websockets
import json

async def run():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        prompt = input("请输入你的问题：")
        # 发送 JSON 格式数据
        await websocket.send(json.dumps({"prompt": prompt}))
        print("\n模型回复（逐段输出）")
        while True:
            msg = await websocket.recv()
            if msg == "[END]":
                print("\n[对话结束]")
                break
            elif msg.startswith("[ERROR]"):
                print("错误：", msg)
                break
            else:
                print(msg, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(run())
