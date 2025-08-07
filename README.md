# 大模型部署实战（手把手带你完成开源大模型的部署搭建）

## 学习资料

### FastAPI 后端框架  （✅）
- **【FastAPI 文档】** [https://fastapi.tiangolo.com/zh/tutorial/](https://fastapi.tiangolo.com/zh/tutorial/)  （待）
- **【附加视频】** [https://www.bilibili.com/video/BV1Ya4y1D7et/](https://www.bilibili.com/video/BV1Ya4y1D7et/?spm_id_from=333.1007.top_right_bar_window_default_collection.content.click&vd_source=7397b776b1946eeca106501c532db604)（ing）
- **【附加文档】** http://blog.yuan316.com/course/1/section/1 （ing）
- **【学习视频1】** [Bilibili 教程：FastAPI部署实战](https://www.bilibili.com/video/BV18L41117Dn)  
- **【学习视频2】** https://www.bilibili.com/video/BV1UfWCeREy5
- **【websocket教程】** [python-websocket_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1z7411Z7C7/?vd_source=7397b776b1946eeca106501c532db604)
- **【协程学习】** [协程 GitHub 学习资源](https://github.com/SparksFly8/Learning_Python/tree/master/coroutine)

### 清华ChatGLM2-6B开源大模型部署
- **【FastAPI】** [openai_api.py（官方实现）](https://github.com/THUDM/ChatGLM2-6B/blob/main/openai_api.py)
- **【WebSocket】**  [websocket_api.py（LucienShui 实现）](https://github.com/LucienShui/ChatGLM-6B/blob/main/websocket_api.py)

### 产品化压力测试  （✅）
- **【压测代码示例】** [CSDN: 大模型压测工具实践](https://blog.csdn.net/liuzhenghua66/article/details/139332747)

## 实战

### 任务描述
部署Qwen2.5-0.5B-Instruct大模型，并完成部署和访问。

### 要求：
- 接口采用http接口和websocket长连接两种方式。
- 完成http接口的压力测试。

### 附加 
- 模型地址：https://modelscope.cn/models/qwen/Qwen2.5-0.5B-Instruct
- 注意：qwen1.5以后没有stream_chat接口，可以采用TextStreamer来实现相同的流式输出功能，可以参考这里https://qwen.readthedocs.io/zh-cn/latest/inference/transformers.html。

# Qwen2.5 Demo：HTTP + WebSocket 接口部署与压力测试

## 项目结构
```
/
├── app/
│   ├── model_loader.py         # 模型加载与推理逻辑
│   ├── http_server.py          # HTTP 接口服务（FastAPI）
│   ├── websocket_server.py     # WebSocket 长连接服务
│   └── websocket_client.py     # WebSocket 客户端示例（支持流式接收）
│
├── stress_test/
│   ├── http_test.py            # 并发压力测试脚本（支持可调并发数和持续时间）
│   └── http_single_test.py     # 单次请求测试脚本
│
├── requirements.txt            # Python依赖包列表
└── README.md                   # 本说明文档
```

---

## 环境准备与启动方式

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动 HTTP 接口服务
```bash
uvicorn app.http_server:app --host 127.0.0.1 --port 8000
```

### 3. 启动 WebSocket 服务
```bash
python -m app.websocket_server
```

---

## 接口说明

### HTTP 接口

- **地址**：`http://127.0.0.1:8000/generate`
- **请求示例**（POST）：
```json
{
  "query": "请用一句话介绍你自己"
}
```
- **返回示例**：
```json
{
  "response": "我是一个人工智能助手，擅长回答各种问题。"
}
```

### WebSocket 接口

- **地址**：`ws://127.0.0.1:8765`
- **发送消息格式**：
```json
{
  "query": "请用一句话介绍你自己"
}
```
- **返回格式**：逐段返回字符串，模拟流式输出，结束时发送 `[对话结束]`

- **测试方式**：
```bash
python app/websocket_client.py
```
或使用浏览器 WebSocket 插件（如 Smart WebSocket Client）

---

## 压力测试说明（参考 CSDN 指南）

### 脚本路径：
```
stress_test/http_test.py
```

### 默认配置：
- 并发请求数：10
- 持续时间：60秒

### 修改参数方式：
```python
concurrent_requests = 10  # 并发数
duration = 60             # 测试时长（秒）
```

### 启动测试：
```bash
python stress_test/http_test.py
```

测试结果示例：
```
--- 第 1 个请求 ---
✅ 回复：请用一句话介绍你自己。我叫李华，热爱编程与AI...

--- 第 2 个请求 ---
✅ 回复：...

✅ 共完成 10 个请求，耗时 59.9 秒
```

---

## 如有侵权，联系必删，仅用于学习用途，不做任何商业用途。
