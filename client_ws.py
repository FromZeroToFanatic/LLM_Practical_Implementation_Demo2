import os
import platform
import json
import asyncio
import websockets

WS_URL = "ws://127.0.0.1:8000/ws"

os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'

def build_prompt(history):
    prompt = ""
    for query, response in history:
        prompt += f"\n用户：{query}"
        prompt += f"\nQwen：{response}"
    return prompt


async def chat():
    history = []
    async with websockets.connect(WS_URL) as websocket:
        # 已在main中显示欢迎信息，这里不再重复

        while True:
            query = input("\n用户：")
            if query.strip().lower() == "stop":
                print("已退出程序。")
                break
            if query.strip().lower() == "clear":
                history = []
                os.system(clear_command)
                print("对话历史已清空。")
                continue

            # 发送 query 和历史
            body = {"query": query, "history": history}
            await websocket.send(json.dumps(body, ensure_ascii=False))

            # 流式接收模型输出
            response_text = ""
            while True:
                try:
                    message = await websocket.recv()
                    body = json.loads(message)

                    if body["status"] == 200:
                        # 回答完成
                        history = body["history"]
                        os.system(clear_command)
                        print("欢迎使用 Qwen2.5-0.5B-Instruct（WebSocket 流式对话模式）")
                        print("输入内容即可开始对话，输入 clear 清空屏幕，输入 stop 退出程序。")
                        print(build_prompt(history))
                        break
                    elif body["status"] == 202:
                        # 流式部分回答 - 不重复清空屏幕，只显示当前输入和正在生成的响应
                        partial_response = body.get("response", "")
                        if partial_response:
                            # 先清除当前行
                            print("\033[1A\033[K", end="")
                            print(f"Qwen：{partial_response}", flush=True)
                except websockets.exceptions.ConnectionClosed:
                    print("连接已关闭")
                    break
                except Exception as e:
                    print(f"接收响应异常: {str(e)}")
                    break


def main():
    # 正确设置TERM环境变量以避免警告
    os.environ['TERM'] = os.environ.get('TERM', 'xterm')
    
    # 清理屏幕并显示欢迎信息
    os.system(clear_command)
    print("欢迎使用 Qwen2.5-0.5B-Instruct（WebSocket 流式对话模式）")
    print("输入内容即可开始对话，输入 clear 清空屏幕，输入 stop 退出程序。")
    
    # 运行聊天客户端
    asyncio.run(chat())

if __name__ == "__main__":
    main()