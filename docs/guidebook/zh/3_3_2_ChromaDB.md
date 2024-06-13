## ChromaDB

agentUniverse中已集成ChromaDB相关依赖，您无需额外安装包即可使用ChromaDB的相关功能。
如果您想学习ChromaDB相关的底层原理，您可以查阅ChromaDB的[官方网站](https://www.trychroma.com/)。

### 我可以用ChromaDB做些什么


您可以在[知识组件](2_2_4_知识.md)中使用ChromaDB来存储和查询知识，你可以使用以下方式来创建一个使用ChromaDB的存储组件:
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

上面的代码会创建一个基于ChromaDB的Knowledge，关于Knowledge的具体用法您可以参考[知识组件](2_2_4_知识.md)，或是参考代码`tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge.py`。