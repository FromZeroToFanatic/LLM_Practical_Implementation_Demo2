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

### 清华ChatGLM2-6B开源大模型部署  （✅）
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

## 如有侵权，联系必删，仅用于学习用途，不做任何商业用途。
