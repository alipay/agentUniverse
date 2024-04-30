# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 15:50
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: store.py
from typing import Any, List, Optional
from pydantic import BaseModel

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query


class Store(BaseModel):
    """The basic class for the knowledge store.

    Store of the knowledge, store class is used to store knowledge
    and provide retrieval capabilities,
    vector storage, such as ChromaDB store, or non-vector storage, such as Redis Store.

    Attributes:
        client (Any): The client of the store,
        client is usually used to connect to the storage and provides knowledge insertion,
        update, deletion, and query operations

        async_client (Any): The async client of the store,
        the function is the same as that of the `client` parameter  in asynchronous mode.

        embedding_model (Embedding): The embedding model of the store,
        used to provided embedding operations on texts to generate a list of floats.
    """

    client: Any = None
    async_client: Any = None
    embedding_model: Optional[Embedding] = None

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        """Initialize the store class."""
        super().__init__(**kwargs)
        if self.client is None:
            self.client = self._new_client()
        if self.async_client is None:
            self.async_client = self._new_async_client()

    def _new_client(self) -> Any:
        """Initialize the client."""
        pass

    def _new_async_client(self) -> Any:
        """Initialize the async client."""
        pass

    def query(self, query: Query, **kwargs) -> List[Document]:
        """Query documents."""
        raise NotImplementedError

    async def async_query(self, query: Query, **kwargs) -> List[Document]:
        """Asynchronously query documents."""
        raise NotImplementedError

    def insert_documents(self, documents: List[Document], **kwargs):
        """Insert documents into the store."""
        raise NotImplementedError

    async def async_insert_documents(self, documents: List[Document], **kwargs):
        """Asynchronously insert documents into the store."""
        raise NotImplementedError

    def insert_document(self, document: Document, **kwargs):
        """Insert document into the store."""
        raise NotImplementedError

    async def async_insert_document(self, document: Document, **kwargs):
        """Asynchronously insert document into the store."""
        raise NotImplementedError

    def delete_document(self, document_id: str, **kwargs):
        """Delete the specific document by the document id."""
        raise NotImplementedError

    async def async_delete_document(self, document_id: str, **kwargs):
        """Asynchronously delete the specific document by the document id."""
        raise NotImplementedError

    def upsert_document(self, documents: List[Document], **kwargs):
        """Upsert document into the store."""
        raise NotImplementedError

    async def async_upsert_document(self, documents: List[Document], **kwargs):
        """Asynchronously upsert documents into the store."""
        raise NotImplementedError

    def update_document(self, documents: List[Document], **kwargs):
        """Update document into the store."""
        raise NotImplementedError

    async def async_update_document(self, documents: List[Document], **kwargs):
        """Asynchronously update documents into the store."""
        raise NotImplementedError
