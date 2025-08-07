import requests

# 单个 HTTP 接口请求测试
response = requests.post("http://127.0.0.1:8000/chat", json={
    "prompt": "请用一句话介绍你自己"
})
print("✅ 响应内容：", response.json())
