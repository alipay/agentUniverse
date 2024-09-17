# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/9/14 22:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: chroma_memory.py
import uuid
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional, List, Any

import chromadb
from pydantic import SkipValidation
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection

from agentuniverse.agent.action.knowledge.embedding.embedding_manager import EmbeddingManager
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.util.memory_util import get_memory_tokens


class ChromaMemory(Memory):
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
        metadata = {'gmt_created': datetime.now().isoformat()}
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
            messages: List[Message] = self.to_messages(result=results)
            return self.prune(messages, self.llm_name, True)
        else:
            results = self._collection.get(where=filters, limit=top_k)
            messages: List[Message] = self.to_messages(result=results, sort_by_time=True)
            # prune messages
            return self.prune(messages, self.llm_name)

    def prune(self, message_list: List[Message], llm_name: str,
              prune_from_end: bool = False, **kwargs) -> List[Message]:
        """Prune messages from the memory due to memory max token limitation."""
        if len(message_list) < 1:
            return []
        new_messages = message_list[:]
        # get the number of tokens of the session messages.
        tokens = get_memory_tokens(new_messages, llm_name)
        # truncate the memory if it exceeds the maximum number of tokens
        if tokens > self.max_tokens:
            prune_messages = []
            while tokens > self.max_tokens:
                if prune_from_end:
                    prune_messages.append(new_messages.pop())
                else:
                    prune_messages.append(new_messages.pop(0))
                tokens = get_memory_tokens(new_messages, llm_name)
            summarized_memory = self.summarize_memory(prune_messages, self.max_tokens - tokens)
            if summarized_memory:
                if prune_from_end:
                    new_messages.append(Message(content=summarized_memory))
                else:
                    new_messages.insert(0, Message(content=summarized_memory))
        return new_messages

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
        if hasattr(component_configer, "embedding_model"):
            self.embedding_model = component_configer.embedding_model
        if hasattr(component_configer, "persist_path"):
            self.persist_path = component_configer.persist_path
        return self

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

    def to_messages(self, result: dict, sort_by_time: bool = False) -> List[Message]:
        message_list = []
        if not result or not result['ids']:
            return message_list
        try:
            if self.is_nested_list(result['ids']):
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
            else:
                metadatas = result.get('metadatas', [])
                documents = result.get('documents', [])
                message_list = [
                    Message(
                        content=documents[i],
                        metadata=metadatas[i] if metadatas[i] else None,
                        source=metadatas[i].get('source', '') if metadatas[i] else ''
                    )
                    for i in range(len(result['ids']))
                ]
            if sort_by_time:
                # order by gmt_created desc
                message_list = sorted(
                    message_list,
                    key=lambda msg: msg.metadata.get('gmt_created', ''),
                )
        except Exception as e:
            print('ChromaMemory.to_messages failed, exception= ' + str(e))
        return message_list

    @staticmethod
    def is_nested_list(variable: List) -> bool:
        return isinstance(variable, list) and len(variable) > 0 and isinstance(variable[0], list)
