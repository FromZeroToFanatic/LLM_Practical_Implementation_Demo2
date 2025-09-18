"""
Serving 是指在生产环境中部署和运行模型，以处理实际的用户请求。
benchmark_serving 关注模型在生产环境中的整体性能和稳定性，包括：
1. Scalability: 系统在增加负载时能否有效扩展，保持高性能。
2. Reliability: 系统的可靠性，包括在高负载或异常情况下的稳定性。
3. Resource Utilization: 评估CPU、GPU、内存等资源的使用情况，确保在高效利用资源的同时保持高性能。
4. Latency under Load: 在高并发请求下，系统的延迟表现。
参考：https://blog.csdn.net/liuzhenghua66/article/details/139332747
"""