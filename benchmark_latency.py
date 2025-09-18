"""
Latency 是指从输入数据发送到模型，直到模型返回预测结果之间所花费的时间。
在机器学习模型的评估中，benchmark_latency 主要关注以下方面：
1.Inference Time: 单次推理所需的时间，包括模型加载、数据预处理、推理过程以及后处理。
2.Throughput: 每秒处理的请求数，通常与延迟成反比关系。
3.Consistency: 在不同负载条件下，延迟是否保持稳定，是否存在明显的抖动或延迟尖峰。
参考：https://blog.csdn.net/liuzhenghua66/article/details/139332747
"""
