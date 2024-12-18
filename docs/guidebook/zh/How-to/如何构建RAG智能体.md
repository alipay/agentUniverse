# 如何构建RAG智能体

本教程提供一个在agentUniverse中快速构建一个RAG智能体。案例的完整结构和内容可在[该文档](../样例文档/法律咨询案例.md)中查看，本文档侧重在构建过程的教学，因此省略了部分非必要的内容。

## 案例说明
本案例基于RagPlanner，搭建了一个简单的法律咨询智能体，通过检索民法典和刑法中的相关条例并结合案件背景给出相关的法律建议。
该案例基于千问大模型和DashScope的embedding和rerank功能，使用前需要您在环境变量中配置`DASHSCOPE_API_KEY`。

知识文件的定义如下：
```yaml
name: "law_knowledge"
description: "中国民法与刑法相关的知识库"
stores:
    - "civil_law_chroma_store"
    - "criminal_law_chroma_store"
    - "civil_law_sqlite_store"
    - "criminal_law_sqlite_store"
insert_processors:
    - "recursive_character_text_splitter"
post_processors:
    - "dashscope_reranker"
readers:
    pdf: "default_pdf_reader"

metadata:
  type: 'KNOWLEDGE'
  module: 'sample_standard_app.intelligence.agentic.knowledge.law_knowledge'
  class: 'LawKnowledge'
```

## 构建知识索引

法律书籍原本：
- [民法典.pdf](../../../../sample_standard_app/intelligence/agentic/knowledge/raw_knowledge_file/民法典.pdf)
- [刑法.pdf](../../../../sample_standard_app/intelligence/agentic/knowledge/raw_knowledge_file/刑法.pdf)

### 抽取PDF中的文本内容
因为本案例中，原始文档是pdf格式，因此我们在Knowledge中进行了如下配置：
```yaml
readers:
    pdf: "default_pdf_reader"
```
这样就可以将pdf中的文本抽取出来。如果您想要读取更多格式的文件，您可以参考[Reader组件](../In-Depth_Guides/原理介绍/知识/Reader.md)中的内容

### 拆分长文本
因为原始文档中的文本内容非常长，因此我们需要将其拆分为小的片段。这里我们选用`recursive_character_text_splitter`对其进行拆分，配置如下：
```yaml
insert_processors:
    - "recursive_character_text_splitter"
```
该配置项是一个list形式，可以配置多种处理文档的处理器，这个案例中指定的唯一处理器`recursive_character_text_splitter`会根据指定的分隔符递归的拆分原始文档直到满足指定长度，具体内容可以参考[DocProcessor](../In-Depth_Guides/原理介绍/知识/DocProcessor.md)。该文档中也包含了其它的文档处理器，您可以直接使用或是编写自己的处理器。

### 配置Store
本案例中包含四个Store：民法和刑法分别存储至sqlite以及chromadb中。我们仅以`civil_law_chroma_store`作为例子，其它Store类似。  
`civil_law_chroma_store`配置如下：
```yaml
name: 'civil_law_chroma_store'
description: '保存了中国民法典的所有内容，以文本向量形式存储'
persist_path: '../../db/civil_law.db'
embedding_model: 'dashscope_embedding'
similarity_top_k: 100
metadata:
  type: 'STORE'
  module: 'agentuniverse.agent.action.knowledge.store.chroma_store'
  class: 'ChromaStore'
```

其中`persist_path`指定了数据库本地文件的存储位置，并指定`dashscope_embedding`作为数据库向量化文本的组件，`similarity_top_k`表示召回的文档数量。关于`Store`的具体内容您可以在[该文档](../In-Depth_Guides/原理介绍/知识/Store.md)中查看。

### 执行插入流程
在完成上述的配置后，我们可以执行下面的代码完成知识库的构建：
```python
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager


if __name__ == '__main__':
    AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)
    law_knowledge = KnowledgeManager().get_instance_obj("law_knowledge")
    law_knowledge.insert_knowledge(
        source_path="../resources/刑法.pdf",
        stores=["civil_law_sqlite_store"]
    )
```
我们通过调用`insert_knowledge`方法中的`source_path`指定了需要插入的数据，并通过`stores`参数分别为不同的文档指定了不同的Store，`stores`非必要参数，如果不指定则默认插入所有的store。


## 构建检索流程

### 重排序
我们对知识的后处理流程进行了如下配置：
```yaml
post_processors:
    - "dashscope_reranker"
```
表示我们会调用Dashscope的重排序服务对文档进行重排序。您也可以在这里加入其它的后处理流程。

## 在智能体中使用RAG

```yaml
info:
  name: 'law_rag_agent'
  description: '一个法律顾问，可以根据给出的事件，以及提供的背景知识做出客观的司法判断'
action:
  knowledge:
    - 'law_knowledge'
```
我们将knowledge像这样配置在Agent中的yaml中即可。

完整的案例以及调用方法请参考[文档](../样例文档/法律咨询案例.md)。