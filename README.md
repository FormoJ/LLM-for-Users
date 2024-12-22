# 剧本杀剧本生成器
## 前言
欢迎大家一起加入维护这个开源项目，也可以申请加入我的书生实战营团队，提供免费的算力支持

InternStudio：https://studio.intern-ai.org.cn/

我的团队id：**KbPJkggiNEMT**
## 简介
剧本杀的创作要求内容严谨、完整、有创意且细节丰富，同时需要确保情节逻辑严密。然而，现有的大模型在长文本生成方面存在局限，尤其是在前后文的连贯性和细节处理上容易出现问题。

为了实现剧本的优质快速生成，本项目致力于研发一款专门针对剧本杀创作的AI模型，结合特定的“trick”，优化长文本生成的连贯性与逻辑性，确保剧本的完整性与创意性。通过这一工具，用户可以快速生成高质量的剧本杀剧本，大大提高创作效率，同时保证剧本内容的严谨性和创新性，满足市场对剧本的多元化需求。

## 项目架构 
![项目框架](绘图文件/框架图.png)
## 运行项目
### API运行
1. git clone 本项目源代码
2. 环境搭建
```
conda create -n your_env_name python=3.11
pip install openai phidata python-dotenv
pip install -r requirements.txt
```
3. 前往[硅基流动](https://cloud.siliconflow.cn/i/TxUlXG3u)注册免费的 API，获取 API_KEY
> https://cloud.siliconflow.cn/i/TxUlXG3u

4. 使用从硅基流动获取的 API_KEY 配置下面的指令并执行
```
export API_KEY=sk-xxx  # your api key
export BASE_URL=https://api.siliconflow.cn/v1
export MODEL_NAME=internlm/internlm2_5-7b-chat  # or别的可用模型

python script_writer.py
```
### 本地运行
ing

## 增量预训练

为使Internlm-2.5-7B模型能具有更好的生成剧本杀中角色对话的能力，本项目使用XTuner工具，讲模型在涉案剧本的对话数据集上进行增量预训练

剧本来源：https://github.com/iEdric/chinese-shortscript

对该仓库中的涉案短剧剧本进行基于GPT的对话提取，将提取好的对话整理为如下所示的XTuner微调所需的json格式，整理好的数据已放在./data/pretrain中

```json
[
  {
      "text": "xxx"
  },
  {
      "text": "xxx"
  },
  ...
]
```

XTuner自定义预训练文档：https://xtuner.readthedocs.io/zh-cn/latest/training/custom_pretrain_dataset.html

对话提取所使用方法：https://github.com/KMnO4-zx/extract-dialogue

自行下载Internlm-2.5-7B模型放在./models中，运行如下命令即可开始增量预训练，该命令详解请参考XTuner文档

```bash
# 请将NPROC_PER_NODE设为您要使用的GPU数量，${SAVE_PATH}更改为您指定的保存路径
NPROC_PER_NODE=1 xtuner train ./configs/pretrain.py --deepspeed deepspeed_zero1 --work-dir ${SAVE_PATH}
```

## 项目进展
### 近期工作
1. 改进人物剧情生成方式
2. 线索搜证、圆桌与解析加入加入人物部分剧情作为prompt
3. 实现以下三个内容由用户输入而不由AI考虑**mode**:
剧本简介、剧本人数、(剧本类型)
4. 改进生成的md文档
### 未来工作
1. 完善本地大模型模式
-  使用RAG提供外部资料学习库  地址：https://github.com/iEdric/chinese-shortscript
-  更加合理的方式微调
2. 优化剧本生成，例如优化prompt
3. 进行模型量化、模型部署与前端页面展示

# 致谢
- 感谢上海人工智能实验室提供的算力支持！！！
- 感谢《一键写书》REPO提供的灵感和开源代码支持！！！

《一键写书》项目地址：https://github.com/langgptai/BookAI

书生大模型学习资料链接：
https://github.com/InternLM/Tutorial

# 参考文档：
- [剧本杀入门：最完整详细模板](https://mp.weixin.qq.com/s/mLJ09J9pB2MwpyjQsEQDfQ)
- https://github.com/InternLM/Tutorial/blob/camp4/docs/L1/Prompt/practice.md
- https://github.com/iEdric/chinese-shortscript
- https://github.com/TeamWiseFlow/awada
- https://github.com/KMnO4-zx/extract-dialogue
- https://xtuner.readthedocs.io/zh-cn/latest/training/custom_pretrain_dataset.html
