# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 15:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: knowledge.py
from typing import Optional, Dict, List, Any

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.store import Store
from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.configers.knowledge_configer import KnowledgeConfiger


class Knowledge(ComponentBase):
    """The basic class for knowledge model.

    Attributes:
        name (str): The name of the knowledge.

        description (str): The description of the knowledge.

        store (Store): The store of the knowledge, which is used to store knowledge
            and provide retrieval capabilities, such as ChromaDB store or Redis Store.

        reader (Reader): The reader of the knowledge, which is used to load data and generate knowledge.

        ext_info (Optional[Dict]): The extended information of the knowledge.
    """

    name: str = ""
    description: Optional[str] = None
    store: Store = None
    reader: Reader = None
    ext_info: Optional[Dict] = None

    def __init__(self, **kwargs):
        super().__init__(component_type=ComponentEnum.KNOWLEDGE, **kwargs)

    def insert_knowledge(self, **kwargs) -> None:
        """Insert the knowledge.

        Load data by the reader and insert the documents into the store.
        """
        document_list: List[Document] = self.reader.load_data()
        self.store.insert_documents(document_list, **kwargs)

    def query_knowledge(self, **kwargs) -> List[Document]:
        """Query the knowledge.

        Query documents from the store and return the results.
        """
        query = Query(**kwargs)
        return self.store.query(query)

    def get_instance_code(self) -> str:
        """Return the full name of the knowledge."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f'{appname}.{self.component_type.value.lower()}.{self.name}'

    def initialize_by_component_configer(self, component_configer: KnowledgeConfiger) -> 'Knowledge':
        """Initialize the Knowledge by the ComponentConfiger object.
        Args:
            component_configer(KnowledgeConfiger): the ComponentConfiger object
        Returns:
            Knowledge: the Knowledge object
        """
        if component_configer.name:
            self.name = component_configer.name
        if component_configer.description:
            self.description = component_configer.description
        if component_configer.ext_info:
            self.ext_info = component_configer.ext_info
        return self
