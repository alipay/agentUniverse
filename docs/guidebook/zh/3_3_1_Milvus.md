## Milvus
如果您想在aU中使用Milvus 向量数据库的话您需要：

1. 安装Milvus向量数据库  
您可以参考[Milvus官方安装文档](https://milvus.io/docs/install_standalone-docker.md)安装并使用Milvus。我们推荐在Docker中启动Milvus容器的方式：
```shell
# Download the installation script
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh

# Start the Docker container
$ bash standalone_embed.sh start
```
这两行命令会拉取Milvus的镜像并启动一个容器，在19530端口上提供数据库服务。
更多详细内容及其它安装方式请参考官方文档。

2. 安装milvus的python sdk
```shell
pip install pymilvus
````

### 我可以用Milvus做些什么

您可以在[知识组件](2_2_4_知识.md)中使用Milvus来存储和查询知识，你可以使用以下方式来创建一个使用Milvus的存储组件:
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

上面的代码会创建一个基于Milvus的Knowledge，关于Knowledge的具体用法您可以参考[知识组件](2_2_4_知识.md)，或是参考代码`tests/test_agentuniverse/unit/agent/action/knowledge/test_knowledge_with_milvus.py`。
