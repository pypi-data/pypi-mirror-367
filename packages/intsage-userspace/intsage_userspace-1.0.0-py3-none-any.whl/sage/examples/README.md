# SAGE 示例集合 (sage-examples)

本目录包含了SAGE框架的各种示例，采用**简单明了**的功能分类，方便用户快速找到需要的示例。

## 📚 目录结构

```
sage-examples/
├── src/                # 示例代码
│   ├── tutorials/      # 基础教程和入门示例
│   ├── rag/            # RAG (检索增强生成) 相关示例
│   ├── agents/         # 多智能体系统示例
│   ├── streaming/      # 流处理和实时数据示例  
│   ├── memory/         # 内存管理和持久化示例
│   └── evaluation/     # 评估和基准测试工具
├── resources/          # 资源文件
│   ├── config/         # 配置文件
│   └── data/           # 示例数据
└── README.md
```

## 🚀 快速开始

### 🔰 初学者 - 从教程开始
```bash
# 1. 框架基础
cd src/tutorials && python hello_world.py

# 2. 核心API学习
cd src/tutorials/core-api && python batch_operator_examples.py
```

### 🧠 RAG开发者
```bash
# 1. 简单RAG入门
cd src/rag && python rag_simple.py

# 2. 探索不同检索策略
python qa_dense_retrieval.py      # 稠密检索
python qa_bm25_retrieval.py       # 稀疏检索
```

### 🤖 智能体开发者
```bash
cd src/agents && python multiagent_app.py
```

### 🌊 流处理开发者
```bash
cd src/streaming && python kafka_query.py
```

## 🔧 路径配置

### Python代码中的配置引用
```python
# 从 src/rag/ 目录运行时
config = load_config("../../resources/config/config.yaml")
```

### 配置文件中的数据引用
```yaml
# 在 resources/config/*.yaml 中
source:
  data_path: "../data/sample/question.txt"
```

## 📚 详细文档

- [结构说明](STRUCTURE.md) - 详细的目录结构文档
- [配置文件说明](resources/config/README.md) - 配置系统详解
- [数据文件说明](resources/data/README.md) - 数据使用指南
- [资源管理](resources/README.md) - 资源目录总览

---

💡 **提示**: 每个子目录都有对应的README文件，包含更详细的使用说明和示例介绍。
