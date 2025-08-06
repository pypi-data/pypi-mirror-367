# 示例数据 (Example Data)

本目录包含SAGE框架示例所需的测试数据和数据集。

## 📁 数据结构

### 📄 sample/ - 基础示例数据
用于测试和演示的小规模数据文件：

- `question.txt` - 标准问题列表，用于大多数RAG示例
- `question1.txt` - 替代问题列表，用于对比测试
- `one_question.txt` - 单个问题，用于快速测试
- `evaluate.json` - 评估数据，包含问题-答案对

### 🧠 neuromem_datasets/ - 神经记忆数据集
专用于内存和认知相关的实验数据：
- `locomo_dataloader.py` - Locomo数据集加载器
- 相关的内存实验数据文件

### 📝 文本文件
- `hubei.txt` - 中文文本示例
- `q.txt` - 简单问题文件

## 🎯 数据用途

### 📊 RAG示例数据
```yaml
# 在配置文件中引用
source:
  data_path: "../data/sample/question.txt"  # 从rag/目录运行时
```

### 🧪 评估数据
```json
// evaluate.json 格式示例
{
  "question": "什么是机器学习？",
  "reference": "机器学习是人工智能的一个分支..."
}
```

### 💾 内存实验数据
用于测试内存系统和知识库构建功能的专业数据集。

## 🔧 数据路径配置

由于data目录现在位于sage-examples内，所有配置文件中的路径都已更新：

### 原路径（已废弃）
```yaml
data_path: "data/sample/question.txt"  # 从根目录引用
```

### 新路径（当前使用）
```yaml
data_path: "../data/sample/question.txt"  # 从示例子目录引用
```

## 📚 添加自定义数据

### 1. 文本数据
```bash
# 添加新的问题文件
echo "你的问题1\n你的问题2" > sample/my_questions.txt
```

### 2. 评估数据
```json
// 创建新的评估文件
[
  {
    "question": "自定义问题",
    "reference": "标准答案"
  }
]
```

### 3. 更新配置
```yaml
# 在配置文件中引用新数据
source:
  data_path: "../data/sample/my_questions.txt"
```

## 🔍 数据格式说明

### 问题文件格式
```
问题1
问题2
问题3
```

### 评估数据格式
```json
{
  "question": "问题文本",
  "reference": "参考答案",
  "category": "分类标签（可选）",
  "difficulty": "难度等级（可选）"
}
```

## 🚀 快速测试

### 验证数据可用性
```bash
# 检查数据文件
ls -la sample/
cat sample/question.txt | head -5

# 测试配置路径
cd ../rag
python -c "
from sage.utils.config.loader import load_config
config = load_config('../config/config.yaml')
print('数据路径:', config['source']['data_path'])
"
```

## 🔗 相关资源

- [配置文件说明](../config/README.md)
- [示例运行指南](../README.md)
- [数据处理文档](../../docs/data-processing.md)
