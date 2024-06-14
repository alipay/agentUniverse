## ChromaDB

The agentUniverse already integrates ChromaDB-related dependencies, so you do not need to install additional packages to use ChromaDB's features.
If you want to learn about the underlying principles of ChromaDB, you can visit the [official ChromaDB website](https://www.trychroma.com/).

### What can I do with ChromaDB?


You can use ChromaDB in the [Knowledge component](2_2_4_Knowledge.md) to store and query knowledge. You can create a storage component using ChromaDB with the following method:
```python
from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore


init_params = dict()
init_params['name'] = 'test_knowledge'
init_params['description'] = 'test_knowledge_description'
init_params['store'] = ChromaStore(collection_name="test_knowledge", embedding_model=OpenAIEmbedding(
    embedding_model_name='text-embedding-ada-002'))
knowledge = Knowledge(**init_params)
```

The above code will create a Knowledge component based on ChromaDB. For more details on how to use the Knowledge component, you can refer to the [Knowledge component](2_2_4_Knowledge.md)，or check the code in `tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge.py`。
