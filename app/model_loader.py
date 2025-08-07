from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer

model_id = "qwen/Qwen2.5-0.5B-Instruct"

# 加载 tokenizer（分词器）
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# 加载模型（在 CPU 上运行）
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to("cpu")

# 文本流式输出对象（配合 WebSocket 客户端使用）
streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)


def generate_text(prompt: str) -> str:
    """使用模型生成回复"""
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=512)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
