# 剧本杀生成器
## 简介
剧本杀的生成需要严谨、完整、有创意、注重细节、丰富、有逻辑，而现在大模型长文本的生成由于注意力机制的特性，无法对长文本进行前后文有效的生成，因此想做一个具有商业倾向的项目，力求对剧本杀剧本生成进行完善，完整

## 运行项目

1. 前往[硅基流动](https://cloud.siliconflow.cn/i/TxUlXG3u)注册免费的 API，获取 API_KEY
> https://cloud.siliconflow.cn/i/TxUlXG3u

4. 使用从硅基流动获取的 API_KEY 配置下面的指令并执行
```
export API_KEY=sk-xxx
export BASE_URL=https://api.siliconflow.cn/v1
export MODEL_NAME=internlm/internlm2_5-7b-chat

python script_writer.py
```

以下是书生大模型学习资料链接：
https://github.com/InternLM/Tutorial

参考文档：https://github.com/InternLM/Tutorial/blob/camp4/docs/L1/Prompt/practice.md
