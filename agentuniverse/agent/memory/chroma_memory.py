# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/14 22:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chroma_memory.py
import uuid
from urllib.parse import urlparse
from typing import Optional, List, Any, Union

import chromadb
from chromadb import QueryResult, GetResult
from pydantic import SkipValidation
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.util.memory_util import get_memory_tokens


class ChromaMemory(Memory):
    llm_name: Optional[str] = None
    collection_name: Optional[str] = 'memory'
    persist_path: Optional[str] = None
    embedding_model: Optional[str] = None
    _collection: SkipValidation[Collection] = None

    def delete(self, session_id: str = '', agent_id: str = '', source: str = '', **kwargs) -> None:
        """Delete the memory from the database."""
        if self._collection is None:
            self._init_collection()
        filters = {}
        if session_id:
            filters['session_id'] = session_id
        if agent_id:
            filters['agent_id'] = agent_id
        if source:
            filters['source'] = source
        self._collection.delete(where=filters)

    def add(self, message_list: List[Message], session_id: str = '', agent_id: str = '', **kwargs) -> None:
        """Add messages to the memory db."""
        if self._collection is None:
            self._init_collection()
        if message_list is None:
            return
        metadata = {}
        if session_id:
            metadata['session_id'] = session_id
        if agent_id:
            metadata['agent_id'] = agent_id
        for message in message_list:
            embedding = []
            if self.embedding_model:
                embedding = EmbeddingManager().get_instance_obj(
                    self.embedding_model
                ).get_embeddings([message.content])[0]
            if message.source:
                metadata['source'] = message.source
            self._collection.add(
                ids=[str(uuid.uuid4())],
                documents=[message.content],
                metadatas=[metadata],
                embeddings=[embedding] if len(embedding) > 0 else None,
            )

    def get(self, session_id: str = '', agent_id: str = '', source: str = '', input: str = '', top_k=10, **kwargs) -> \
            List[Message]:
        """Get messages from the memory db."""
        if self._collection is None:
            self._init_collection()
        filters = {}
        if session_id:
            filters['session_id'] = session_id
        if agent_id:
            filters['agent_id'] = agent_id
        if source:
            filters['source'] = source
        if input:
            embedding = []
            if self.embedding_model:
                embedding = EmbeddingManager().get_instance_obj(
                    self.embedding_model
                ).get_embeddings([input])[0]
            if len(embedding) > 0:
                results = self._collection.query(
                    query_embeddings=embedding, where=filters, n_results=top_k
                )
            else:
                results = self._collection.query(query_texts=[input], where=filters, n_results=top_k)
        else:
            results = self._collection.get(where=filters, limit=top_k)
        messages: List[Message] = self.to_messages(results)
        # prune messages
        return self.prune(messages, self.llm_name)

    def prune(self, message_list: List[Message], llm_name: str, **kwargs) -> List[Message]:
        """Prune messages from the memory due to memory max token limitation."""
        if len(message_list) < 1:
            return []
        prune_messages = message_list[:]
        # get the number of tokens of the session messages.
        tokens = get_memory_tokens(prune_messages, llm_name)
        # truncate the memory if it exceeds the maximum number of tokens
        if tokens > self.max_tokens:
            while tokens > self.max_tokens:
                prune_messages.pop(0)
                tokens = get_memory_tokens(prune_messages, llm_name)
        return prune_messages

    def initialize_by_component_configer(self, component_configer: MemoryConfiger) -> 'ChromaMemory':
        """Initialize the memory by the ComponentConfiger object.
        Args:
            component_configer(MemoryConfiger): the ComponentConfiger object
        Returns:
            ChromaMemory: the ChromaMemory object
        """
        super().initialize_by_component_configer(component_configer)
        if hasattr(component_configer, "collection_name"):
            self.collection_name = component_configer.collection_name
        if hasattr(component_configer, "llm_name"):
            self.llm_name = component_configer.llm_name
        if hasattr(component_configer, "embedding_model"):
            self.embedding_model = component_configer.embedding_model
        if hasattr(component_configer, "persist_path"):
            self.persist_path = component_configer.persist_path
        return self

    def set_by_agent_model(self, **kwargs):
        """ Assign values of parameters to the ChromaMemory model in the agent configuration."""
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'llm_name' in kwargs and kwargs['llm_name']:
            copied_obj.llm_name = kwargs['llm_name']
        return copied_obj

    def _init_collection(self) -> Any:
        if self.persist_path.startswith('http') or \
                self.persist_path.startswith('https'):
            parsed_url = urlparse(self.persist_path)
            settings = Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=parsed_url.hostname,
                chroma_server_http_port=str(parsed_url.port)
            )
        else:
            settings = Settings(
                is_persistent=True,
                persist_directory=self.persist_path
            )
        client = chromadb.Client(settings)
        self._collection = client.get_or_create_collection(name=self.collection_name)
        return client

    @staticmethod
    def to_messages(result: Union[QueryResult, GetResult]) -> List[Message]:
        if not result or not result['ids']:
            return []

        metadatas = result.get('metadatas', [[]])
        documents = result.get('documents', [[]])

        message_list = [
            Message(
                content=documents[0][i],
                metadata=metadatas[0][i] if metadatas[0] else None,
                source=metadatas[0][i].get('source', '') if metadatas[0] else ''
            )
            for i in range(len(result['ids'][0]))
        ]

        return message_list
