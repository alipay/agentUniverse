## ChromaDB

The agentUniverse already integrates ChromaDB-related dependencies, so you do not need to install additional packages to use ChromaDB's features.
If you want to learn about the underlying principles of ChromaDB, you can visit the [official ChromaDB website](https://www.trychroma.com/).

### How to Configure ChromaDB Components
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
- persist_path: The persistence storage path for the database, used for storing and loading vector data.
- embedding_model: The model used to generate embedding vectors, specified here as dashscope_embedding.
- similarity_top_k: The number of most similar results returned in similarity search.

### Usage
[Knowledge_Define_And_Use](2_2_4_Knowledge_Define_And_Use.md)