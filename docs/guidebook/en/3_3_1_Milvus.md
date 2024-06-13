## Milvus
If you want to use the Milvus vector database in aU, you need to:

1. Install the Milvus vector database
You can refer to the [official Milvus installation documentation](https://milvus.io/docs/install_standalone-docker.md) to install and use Milvus. We recommend starting the Milvus container in Docker with the following commands:
``` shell
# Download the installation script
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh

# Start the Docker container
$ bash standalone_embed.sh start
```
These two commands will pull the Milvus image and start a container, providing database services on port 19530. For more details and other installation methods, please refer to the official documentation.

2. Install the Milvus Python SDK
```
pip install pymilvus
```

### What can I do with Milvus

You can use Milvus in the [Knowledge component](2_2_4_Knowledge.md) to store and query knowledge. You can create a storage component using Milvus as follows:

```python
from agentuniverse.agent.action.knowledge.store.milvus_store import MilvusStore
from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding
from agentuniverse.agent.action.knowledge.knowledge import Knowledge

init_params = {}
init_params['name'] = 'test_knowledge'
init_params['description'] = 'test_knowledge_description'
init_params['store'] = MilvusStore(
    connection_args={"host": "localhost", "port": "19530"},
    collection_name="test_knowledge", 
    embedding_model=OpenAIEmbedding(
            embedding_model_name='text-embedding-ada-002'
    )
)
knowledge = Knowledge(**init_params)
```

The above code will create a Milvus-based Knowledge instance. For detailed usage of Knowledge, you can refer to the [Knowledge component](2_2_4_Knowledge.md) or the code `tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_with_milvus.py`.
