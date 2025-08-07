import requests
import time
import threading

# 要发送的请求数量（并发线程数）
num_requests = 2

def send_request(idx):
    try:
        print(f"\n--- 第 {idx+1} 个请求 ---")
        res = requests.post("http://127.0.0.1:8000/chat", json={"prompt": "请用一句话介绍你自己"})
        print("✅ 回复：", res.json()["response"][:100], "...")
    except Exception as e:
        print("请求失败：", e)

# 多线程并发测试（模仿压力测试）
start = time.time()
threads = []
for i in range(num_requests):
    t = threading.Thread(target=send_request, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print(f"\n共完成 {num_requests} 个请求，耗时 {time.time() - start:.2f} 秒")
