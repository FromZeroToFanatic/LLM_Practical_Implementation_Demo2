import os
import platform
import requests
import os
import json

API_URL = "http://127.0.0.1:8000/v1/chat/completions"
MODEL = "qwen/Qwen2.5-0.5B-Instruct"

os_name = platform.system()
clear_command = 'cls' if os_name == 'Windows' else 'clear'


def build_prompt(history):
    prompt = "欢迎使用 Qwen2.5-0.5B-Instruct，clear 清空对话历史，stop 终止程序"
    for h in history:
        prompt += f"\n\n用户：{h['query']}"
        prompt += f"\n\nQwen：{h['response']}"
    return prompt


def main():
    # 设置TERM环境变量以避免警告
    os.environ.get('TERM', 'xterm')
    
    history = []
    print("欢迎使用 Qwen2.5-0.5B-Instruct，clear 清空对话历史，stop 终止程序")
    while True:
        query = input("\n用户：")
        if query == "stop":
            break
        if query == "clear":
            history = []
            os.system(clear_command)
            print("欢迎使用 Qwen2.5-0.5B-Instruct，输入内容即可进行对话，clear 清空对话历史，stop 终止程序")
            continue

        # 让用户选择是否使用流式请求
        if query.startswith('stream'):
            stream_mode = True
            query = query[7:].strip()
            if not query:
                print("请在stream后输入您的问题")
                continue
        else:
            stream_mode = False

        # 构造符合OpenAI API格式的请求体
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": query}],
            "temperature": 0.7,
            "top_p": 0.9,
            "max_length": 512,
            "stream": stream_mode
        }

        try:
            if stream_mode:
                # 流式请求处理
                response = requests.post(API_URL, json=payload, stream=True, timeout=300)
                if response.status_code == 200:
                    content = ""
                    os.system(clear_command)
                    print(build_prompt(history) + f"\n\n用户：{query}\n\nQwen：", end="", flush=True)
                    
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line == "[DONE]":
                                break
                            try:
                                if line.startswith("data: "):
                                    line = line[6:]
                                json_line = json.loads(line)
                                if "choices" in json_line:
                                    delta = json_line["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        content += delta["content"]
                                        print(delta["content"], end="", flush=True)
                            except json.JSONDecodeError:
                                continue
                    
                    print()
                    history.append({"query": query, "response": content})
                else:
                    print(f"请求失败: {response.status_code} {response.text}")
            else:
                # 非流式请求处理
                response = requests.post(API_URL, json=payload, timeout=300)
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    history.append({"query": query, "response": content})
                    os.system(clear_command)
                    print(build_prompt(history), flush=True)
                else:
                    print(f"请求失败: {response.status_code} {response.text}")
        except Exception as e:
            print(f"请求异常: {str(e)}")


if __name__ == "__main__":
    main()
