# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/30 10:22
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: milvus_store.py
from typing import List, Optional

try:
    from pymilvus import connections, Collection, CollectionSchema, \
        FieldSchema, DataType, utility
except ImportError as e:
    raise ImportError(
        "pymilvus is not installed. Please install it with 'pip install pymilvus'") from e

from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store

DEFAULT_CONNECTION_ARGS = {
    "host": "localhost",
    "port": "19530"
}

DEFAULT_SEARCH_ARGS = {
    "metric_type": "L2",
    "params": {"nprobe": 10}
}

DEFAULT_INDEX_PARAMS = {
    "metric_type": "L2",
    "index_type": "HNSW",
    "params": {"M": 8, "efConstruction": 64},
}


class MilvusStore(Store):
    collection_name: Optional[str] = 'milvus_db'
    collection: Collection = None
    connection_name: str = 'default_connection'

    def __init__(
            self,
            connection_args: dict = None,
            **kwargs
    ):
        """Initialize the Milvus store class."""
        super().__init__(**kwargs)
        if not connection_args:
            connection_args = DEFAULT_CONNECTION_ARGS
        host = connection_args["host"]
        port = connection_args["port"]
        db_name = connection_args.get("db_name", "default")
        self.connection_name = f"{host}_{port}_{db_name}"
        self._connect_to_milvus(connection_args)
        if utility.has_collection(self.collection_name,
                                  using=self.connection_name):
            self.collection = Collection(
                self.collection_name, using=self.connection_name
            )
            self.collection.load()


    def _connect_to_milvus(self, connection_args: dict):
        """Connect to Milvus server."""
        if not connections.has_connection(self.connection_name):
            connections.connect(
                alias=self.connection_name, **connection_args
            )

    def _create_or_load_collection(self,
                                   dim: int = 128,
                                   max_length: int = 65535,
                                   index_params: dict = None):
        """
        Create a new collection or load an existing collection.

        This method handles the creation of a new collection with specified parameters
        or loads an existing collection if it already exists. Collections are used
        to store data with specific dimensional attributes and indexing parameters.

        Parameters:
        - dim (int): The dimension of the collection, default is 128.
        - max_length (int): The maximum length of the collection, default is 65535.
        - index_params (dict, optional): Additional parameters for indexing. This
          dictionary can include specific configurations for the index creation or loading.

        Returns:
        None
        """
        if utility.has_collection(self.collection_name,
                                  using=self.connection_name):
            self.collection = Collection(
                self.collection_name, using=self.connection_name
            )
        else:
            if not index_params:
                index_params = DEFAULT_INDEX_PARAMS
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100,
                            is_primary=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR,
                            dim=dim),
                FieldSchema(name="text", dtype=DataType.VARCHAR,
                            max_length=max_length),
                FieldSchema(name="metadata", dtype=DataType.JSON)
            ]
            schema = CollectionSchema(fields, "Milvus collection schema")
            self.collection = Collection(self.collection_name, schema,
                                         using=self.connection_name)
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            self.collection.load()

    def query(self,
              query: Query,
              search_args: dict = None,
              **kwargs) -> List[Document]:
        """
        Query the Milvus collection with the given query and return the top k results.

        Parameters:
        - query (Query): The query object that contains the parameters and data for the search.
        - search_args (dict, optional): A dictionary of additional arguments for the search.
          This can include parameters such as the number of results to return, specific search
          algorithms, or other configurations.

        Returns:
        - List[Document]: A list of Document objects that are the top k results from the query.
        """
        if not self.collection:
            return self.to_documents([])
        embedding = query.embedding
        if self.embedding_model is not None and len(embedding) == 0:
            embedding = self.embedding_model.get_embeddings([query.query_str])[
                0]
        if not search_args:
            search_args = DEFAULT_SEARCH_ARGS
        if len(embedding) > 0:
            query_result = self.collection.search(
                data=[embedding],
                anns_field="embedding",
                param=search_args,
                limit=query.similarity_top_k,
                output_fields=["id", "text", "embedding", "metadata"]
            )
        else:
            query_result = []
        return self.to_documents(query_result)


    def upsert_document(self,
                        documents: List[Document],
                        max_length: int = 65535,
                        index_params: dict = None,
                        **kwargs):
        """
        This method inserts new documents or updates existing documents in the collection.
        The upsert operation ensures that the documents are either added if they do not
        already exist or updated if they do.

        Parameters:
        - documents (List[Document]): A list of Document objects to be upserted into the collection.
        - max_length (int): The maximum length of the collection, default is 65535.
        - index_params (dict, optional): Additional parameters for indexing. This dictionary
          can include specific configurations for the index creation or updating.

        Returns:
        None
        """
        for document in documents:
            embedding = document.embedding
            if self.embedding_model is not None and len(embedding) == 0:
                embedding = self.embedding_model.get_embeddings([document.text])[0]
            if not self.collection:
                self._create_or_load_collection(
                    dim=len(embedding),
                    max_length=max_length,
                    index_params=index_params
                )
            expr = f'id == "{document.id}"'
            existing_docs = self.collection.query(expr)
            entities = [
                [document.id],
                [embedding],
                [document.text],
                [document.metadata]
            ]
            if existing_docs:
                self.collection.delete(expr)
                self.collection.insert(entities)
            else:
                self.collection.insert(entities)
            self.collection.load()

    def insert_documents(self,
                         documents: List[Document],
                         max_length: int = 65535,
                         index_params: dict = None,
                         ):
        """Insert documents to the Milvus collection."""
        self.upsert_document(documents, max_length, index_params)

    def update_document(self, documents: List[Document], **kwargs):
        """Update document into the store."""
        self.upsert_document(documents)

    @staticmethod
    def to_documents(query_result) -> List[Document]:
        """Convert the query results of Milvus to the AgentUniverse(AU)
        document format."""
        if query_result is None:
            return []
        documents = []
        for result in query_result:
            for res in result:
                documents.append(Document(
                    id=res.fields.get("id"),
                    text=res.fields.get("text"),
                    embedding=res.fields.get("embedding")
                    if res.fields.get("embedding") else [],
                    metadata=res.fields.get("metadata")
                    if res.fields.get("metadata") else None)
                )
        return documents
