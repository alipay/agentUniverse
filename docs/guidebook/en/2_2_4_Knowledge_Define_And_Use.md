# How to Define the Knowledge Component
Based on the design features of agentUniverse domain components, creating a knowledge definition involves two parts:

* knowledge_xx.yaml
* knowledge_xx.py

The `knowledge_xx.yaml` file contains important information about the knowledge component such as its name, description, loading method, storage method, etc., while the `knowledge_xx.py` file contains the specific definitions of the knowledge. Understanding this principle, let's delve into how to create these two parts.

## Creating the Knowledge Configuration - knowledge_xx.yaml
We will detail the various components in the configuration.

### Setting Basic Attributes of Knowledge
* `name`:  The name of the knowledge, which you can set to any name you prefer.
* `description`:  A description of the knowledge, filled according to your actual needs.
* `store`: The storage medium for the knowledge (e.g., ChromaStore, RedisStore, FaissStore, etc.)
* `reader`: Represents the method of reading the knowledge (e.g., FileReader, UrlReader, etc.)
* `ext_info`: Extended parameters

### Setting Knowledge Component Metadata
**`metadata` - Component Metadata**
* `type` : Component type, 'KNOWLEDGE'
* `module`: The package path of the knowledge entity
* `class`: The class name of the knowledge entity

### A Sample Knowledge Configuration
```yaml
name: 'demo_knowledge'
description: 'demo knowledge'
metadata:
  type: 'KNOWLEDGE'
  module: 'sample_standard_app.app.core.knowledge.demo_knowledge'
  class: 'DemoKnowledge'
```

The above is an actual sample of a Knowledge configuration. 

Besides, the standard configuration items introduced above, you can find more knowledge configuration YAML samples in our sample project under the path `sample_standard_app.app.core.knowledge`. 

Additionally, agentUniverse does not restrict users from extending the knowledge YAML configuration content. You can create any custom configuration keys according to your requirements, but please be mindful not to use the same names as the default configuration keywords mentioned above.

## Creating the Knowledge Domain Behavior Definition - knowledge_xx.py

### Creating a Knowledge Class Object
Create the corresponding Knowledge class object and inherit the base class Knowledge from the agentUniverse framework. 

### Setting Up the Reader Module
The Reader module is responsible for reading the knowledge, and this part is optional. agentUniverse currently has built-in Readers for the following data formats:

* DocxReader
* PdfReader
* PptxReader
* WebPdfReader
* FileReader

Their paths are located under `agentuniverse.agent.action.knowledge.reader.file`. The Reader module supports customization, and you can write your own Reader's loading methods.

### Setting Up the Store Module
The Store module is responsible for the persistence interaction of the knowledge, performing operations like insertion, reading, deletion, and updating of the knowledge. This part is optional as well. agentUniverse currently has built-in Stores for the following data formats:

* ChromaStore
* MilvusStore

Their paths are located under `agentuniverse.agent.action.knowledge.store`. The Store module supports customization, and you can write your own Store's loading methods.

### Defining the query_knowledge Method
This method is responsible for querying the corresponding knowledge. Its default implementation uses the Store function queries, but users can override it based on their actual needs.

```python
def query_knowledge(self, **kwargs) -> List[Document]:
    """Query the knowledge.

    Query documents from the store and return the results.
    """
    query = Query(**kwargs)
    return self.store.query(query)
```

### Defining the insert_knowledge Method
This method is responsible for adding new pieces of knowledge, with its default implementation utilizing the insertion operation of the Store function. Users have the flexibility to override this behavior based on their specific requirements.

```python
def insert_knowledge(self, **kwargs) -> None:
    """Insert the knowledge.

    Load data by the reader and insert the documents into the store.
    """
    document_list: List[Document] = self.reader.load_data()
    self.store.insert_documents(document_list, **kwargs)
```

#### A Sample Knowledge Object Definition
```python
from agentuniverse.agent.action.knowledge.embedding.openai_embedding import OpenAIEmbedding
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.reader.file.web_pdf_reader import WebPdfReader
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from langchain.text_splitter import TokenTextSplitter

SPLITTER = TokenTextSplitter(chunk_size=800, chunk_overlap=100)


class DemoKnowledge(Knowledge):
    """The demo knowledge."""

    def __init__(self, **kwargs):
        """The __init__ method.

        Some parameters, such as name and description,
        are injected into this class by the demo_knowledge.yaml configuration.


        Args:
            name (str): Name of the knowledge.

            description (str): Description of the knowledge.

            store (Store): Store of the knowledge, store class is used to store knowledge
            and provide retrieval capabilities, such as ChromaDB store or Redis Store,
            demo knowledge uses ChromaDB as the knowledge storage.

            reader (Reader): Reader is used to load data,
            the demo knowledge uses WebPdfReader to load pdf files from web.
        """
        super().__init__(**kwargs)
        self.store = ChromaStore(collection_name="chroma_store", embedding_model=OpenAIEmbedding(
            embedding_model_name='text-embedding-3-small'), dimensions=1056)
        self.reader = WebPdfReader()
        # initialize the knowledge
        # self.insert_knowledge()

    def insert_knowledge(self, **kwargs) -> None:
        """Insert the knowledge into the knowledge store.

        Step1: Load data from the web using WebPdfReader.
        Step2: Split the data into chunks using TokenTextSplitter().
        Step3: Insert the data into the ChromaStore.

        Note:
            To avoid that the token in the embedding process exceeds the limit, the document needs to be split.
        """
        doc_list = self.reader.load_data('https://www.sfu.ca/~poitras/BUFFET.pdf')
        lc_doc_list = SPLITTER.split_documents(Document.as_langchain_list(doc_list))
        self.store.insert_documents(Document.from_langchain_list(lc_doc_list))
```

## Take Note of the Path Where Your Knowledge Is Located
With the above Knowledge configuration and definition steps, you have mastered all the steps for creating knowledge. Next, we will use this knowledge. Before use, please ensure that the created Knowledge is in the correct package scan path.

In the config.toml file of the agentUniverse project, you need to configure the package corresponding to the Knowledge configuration. Please reconfirm whether the package path of the created file is under the `CORE_PACKAGE`'s `knowledge` path or its subpaths.

For example, in the configuration of the sample project, it is as follows:
```yaml
[CORE_PACKAGE]
# Scan and register knowledge components for all paths under this list, with priority over the default.
knowledge = ['sample_standard_app.app.core.knowledge']
```

# How to Use the Knowledge Component
## Configuring Use in the Agent
Based on the content in [Creating and Using Agents](2_2_1_Agent_Create_And_Use.md), you can set any created knowledge under the knowledge action in the agent.

## Using the Knowledge Manager
You can obtain the Knowledge instance corresponding to the name via the `.get_instance_obj(xx_knowledge_name)` method in the Knowledge Manager, and call it using the `query_knowledge` method.

```python
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManage

knowledge = KnowledgeManager().get_instance_obj(knowledge_name)
knowledge.query_knowledge(**query_input)
```

# Learn More About Existing Knowledge
For more knowledge examples provided by the framework, you can check the `sample_standard_app.app.core.knowledge` package path.

# Conclusion
Now you have mastered the definition and use of the Knowledge component. Go ahead and try creating and using your knowledge.