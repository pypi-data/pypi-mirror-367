# 流处理示例 (Streaming Examples)

这个目录包含实时数据流处理和事件驱动的应用示例，展示SAGE框架在流式数据处理场景下的能力。

## 📁 文件列表

### `kafka_query.py`
Kafka流处理示例，展示：
- Kafka数据源的连接和消费
- 实时数据流的处理
- 流式查询和响应

#### 功能特点：
- 实时数据摄取
- 流式数据转换
- 低延迟响应

### `multiple_pipeline.py` 
多管道并行处理示例，展示：
- 多个数据处理管道的并行执行
- 管道间的数据交换和协调
- 复杂流处理拓扑

#### 架构特点：
- 并行管道处理
- 数据分流和合并
- 动态负载均衡

## 🚀 运行方式

### Kafka流处理
```bash
# 确保Kafka服务运行
python kafka_query.py
```

### 多管道处理
```bash
python multiple_pipeline.py
```

## ⚙️ 配置要求

### Kafka配置
```yaml
kafka:
  bootstrap_servers: ["localhost:9092"]
  topic: "sage_queries"
  group_id: "sage_consumer_group"
```

### 管道配置
```yaml
pipelines:
  pipeline_count: 3
  buffer_size: 1000
  processing_timeout: 30
```

## 🔧 环境准备

### Kafka环境
```bash
# 启动Kafka
bin/kafka-server-start.sh config/server.properties

# 创建主题
bin/kafka-topics.sh --create --topic sage_queries --bootstrap-server localhost:9092
```

## 📊 监控指标

流处理系统提供以下监控指标：
- **吞吐量** - 每秒处理的消息数
- **延迟** - 端到端处理延迟
- **积压** - 待处理消息队列长度
- **错误率** - 处理失败的比例

## 🎯 应用场景

### 实时问答系统
- 用户查询的实时响应
- 知识库的动态更新
- 多用户并发处理

### 数据管道监控
- 数据质量实时检测
- 异常事件的及时告警
- 系统性能的动态调优

## 🔗 相关组件

- [流处理源](../../packages/sage-userspace/src/sage/lib/io/source.py)
- [流处理汇](../../packages/sage-userspace/src/sage/lib/io/sink.py)
- [消息队列集成](../../packages/sage-userspace/src/sage/lib/io/)
