## ChromaDB

agentUniverse中已集成ChromaDB相关依赖，您无需额外安装包即可使用ChromaDB的相关功能。
如果您想学习ChromaDB相关的底层原理，您可以查阅ChromaDB的[官方网站](https://www.trychroma.com/)。

### 如何配置Chromadb组件
```yaml
name: 'chroma_store'
description: 'store based on chroma db'
persist_path: '../../DB/criminal_law.db'
embedding_model: 'dashscope_embedding'
similarity_top_k: 100
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.chroma_store'
  class: 'ChromaStore'
```
- persist_path: 数据库的持久化存储路径，用于存储和加载向量数据。
- embedding_model: 用于生成嵌入向量的模型名称，这里指定为 dashscope_embedding。
- similarity_top_k: 在相似度搜索中返回最相似结果的数量。

### 使用方式
[知识定义与使用](2_2_4_知识定义与使用.md)
