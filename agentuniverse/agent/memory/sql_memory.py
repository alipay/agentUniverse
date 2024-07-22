# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/18 21:08
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: sql_memory.py
from abc import abstractmethod
import datetime
import json
from typing import Optional, List, Any

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import declarative_base
from sqlalchemy import JSON, Integer, String, DateTime, Text, Column, Index

from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message
from agentuniverse.base.config.component_configer.configers.memory_configer import MemoryConfiger
from agentuniverse.base.util.memory_util import get_memory_string
from agentuniverse.database.sqldb_wrapper import SQLDBWrapper
from agentuniverse.database.sqldb_wrapper_manager import SQLDBWrapperManager
from agentuniverse.llm.llm_manager import LLMManager


class BaseMemoryConverter(BaseModel):
    """Convert BaseMemory to the SQLAlchemy model."""

    model_class: Any = None
    model_config = ConfigDict(protected_namespaces=())

    @abstractmethod
    def from_sql_model(self, sql_message: Any) -> Message:
        """Convert a SQLAlchemy model to a Message instance."""
        raise NotImplementedError

    @abstractmethod
    def to_sql_model(self, message: Message, session_id: str) -> Any:
        """Convert a Message instance to a SQLAlchemy model."""
        raise NotImplementedError

    @abstractmethod
    def get_sql_model_class(self) -> Any:
        """Get the SQLAlchemy model class."""
        raise NotImplementedError


def create_memory_model(table_name: str, DynamicBase: Any) -> Any:
    """
    Create a memory model for a given table name.

    Args:
        table_name: The name of the table to use.
        DynamicBase: The base class to use for the model.

    Returns:
        The model class.
    """

    class MemoryModel(DynamicBase):
        """The default memory model for SqlMemory."""
        __tablename__ = table_name
        id = Column(Integer, primary_key=True, autoincrement=True)
        session_id = Column(String(50))
        message = Column(Text)
        meta_data = Column(JSON)
        gmt_create = Column(DateTime, default=datetime.datetime.now)
        gmt_modified = Column(DateTime, default=datetime.datetime.now,
                              onupdate=datetime.datetime.now)
        __table_args__ = (
            Index('ix_session_id', session_id),
        )

    return MemoryModel


class DefaultMemoryConverter(BaseMemoryConverter):
    """The default memory converter for SqlMemory."""

    def __init__(self, table_name: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_class = create_memory_model(table_name, declarative_base())

    def from_sql_model(self, sql_message: Any) -> Message:
        """Convert a SQLAlchemy model to a Message instance."""
        return Message.from_dict(json.loads(sql_message.message))

    def to_sql_model(self, message: Message, session_id: str) -> Any:
        """Convert a Message instance to a SQLAlchemy model."""
        return self.model_class(
            session_id=session_id, message=json.dumps(message.to_dict(), ensure_ascii=False)
        )

    def get_sql_model_class(self) -> Any:
        """Get the SQLAlchemy model class."""
        return self.model_class


class SqlMemory(Memory):
    """SqlMemory class that stores messages in a SQL database.

    Long-term memory: it is a long-term memory that stores messages in a SQL database.

    Attributes:
        llm_name (Optional[str]): The name of the LLM used to calculate the memory tokens.
        sqldb_table_name (str): The name of the table to store for the memory.
        sqldb_wrapper_name (str): The name of the SQLDBWrapper to use for the memory.
        memory_converter (BaseMemoryConverter): The memory converter to use for the memory.
        _sqldb_wrapper (SQLDBWrapper): The SQLDBWrapper instance to use for the memory.
    """

    llm_name: Optional[str] = None
    sqldb_table_name: Optional[str] = 'memory'
    sqldb_wrapper_name: Optional[str] = None
    memory_converter: BaseMemoryConverter = None
    _sqldb_wrapper: SQLDBWrapper = None

    def clear(self, session_id: str = '', **kwargs) -> None:
        """Clear the memory from the database."""
        if self._sqldb_wrapper is None:
            self.init_db()
        with self._sqldb_wrapper.get_session() as session:
            session.query(self.memory_converter.get_sql_model_class()).filter(
                getattr(self.memory_converter.get_sql_model_class(), 'session_id')
                == session_id
            ).delete()
            session.commit()

    def add(self, message_list: List[Message], session_id: str = '', **kwargs) -> None:
        """Add messages to the memory db."""
        if self._sqldb_wrapper is None:
            self.init_db()
        if message_list is None:
            return
        with self._sqldb_wrapper.get_session() as session:
            for message in message_list:
                session.add(self.memory_converter.to_sql_model(message, session_id))
            session.commit()

    def get(self, session_id: str = '', **kwargs) -> List[Message]:
        """Get messages from the memory db."""
        if self._sqldb_wrapper is None:
            self.init_db()
        with self._sqldb_wrapper.get_session() as session:
            # get the messages from the memory by session_id
            result = (
                session.query(self.memory_converter.model_class)
                .where(
                    getattr(self.memory_converter.get_sql_model_class(), 'session_id')
                    == session_id
                )
                .order_by(self.memory_converter.get_sql_model_class().id.asc())
            )
            messages = []
            for record in result:
                messages.append(self.memory_converter.from_sql_model(record))
            # prune the messages
            return self.prune(messages, session_id)

    def prune(self, message_list: List[Message], session_id: str = '', **kwargs) -> List[Message]:
        """Prune messages from the memory due to memory max token limitation."""
        if len(message_list) < 1:
            return []
        prune_messages = message_list[:]
        if self.llm_name:
            # get the number of tokens of the session messages.
            session_message_str = get_memory_string(message_list)
            llm_instance = LLMManager().get_instance_obj(self.llm_name)
            message_tokens = llm_instance.get_num_tokens(session_message_str)

            # truncate the memory if it exceeds the maximum number of tokens
            if message_tokens > self.max_tokens:
                while message_tokens > self.max_tokens:
                    prune_messages.pop(0)
                    message_tokens = llm_instance.get_num_tokens(get_memory_string(prune_messages))
        return prune_messages

    def set_by_agent_model(self, **kwargs):
        """ Assign values of parameters to the Memory model in the agent configuration."""
        # note: default shallow copy
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'llm_name' in kwargs and kwargs['llm_name']:
            copied_obj.llm_name = kwargs['llm_name']
        return copied_obj

    def initialize_by_component_configer(self, component_configer: MemoryConfiger) -> 'SqlMemory':
        """Initialize the memory by the ComponentConfiger object.
        Args:
            component_configer(MemoryConfiger): the ComponentConfiger object
        Returns:
            Memory: the Memory object
        """
        super().initialize_by_component_configer(component_configer)
        if 'sqldb_wrapper_name' in component_configer.configer.value:
            self.sqldb_wrapper_name = component_configer.configer.value.get('sqldb_wrapper_name', '')
        if 'sqldb_table_name' in component_configer.configer.value:
            self.sqldb_table_name = component_configer.configer.value.get('sqldb_table_name', '')
        if self.sqldb_wrapper_name is None:
            raise Exception('`sqldb_wrapper_name` is not set')
        # initialize the memory converter if not set
        if self.memory_converter is None:
            self.memory_converter = DefaultMemoryConverter(self.sqldb_table_name)
        return self

    def init_db(self) -> None:
        """Initialize the database."""
        self._sqldb_wrapper = SQLDBWrapperManager().get_instance_obj(self.sqldb_wrapper_name)
        if self._sqldb_wrapper is None:
            raise Exception('The sqldb_wrapper for the `sqldb_wrapper_name` was not found,'
                            ' please check the `sqldb_wrapper_name`.')
        self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        """Create the db table if it does not exist."""
        with self._sqldb_wrapper.sql_database._engine.connect() as conn:
            if not conn.dialect.has_table(conn, self.sqldb_table_name):
                self.memory_converter.get_sql_model_class().metadata.create_all(
                    self._sqldb_wrapper.sql_database._engine)
