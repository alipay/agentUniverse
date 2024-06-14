# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 19:28
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_knowledge.py

from agentuniverse.agent.action.knowledge.embedding.dashscope_embedding import DashscopeEmbedding
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.reader.file.pdf_reader import PdfReader
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from langchain.text_splitter import TokenTextSplitter
from pathlib import Path

SPLITTER = TokenTextSplitter(chunk_size=600, chunk_overlap=100)


class CriminalLawKnowledge(Knowledge):
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
        self.store = ChromaStore(
            collection_name="law_store",
            persist_path="../../DB/criminal_law.db",
            embedding_model=DashscopeEmbedding(
                embedding_model_name='text-embedding-v2'
            ),
            dimensions=1536)
        self.reader = PdfReader()
        # Initialize the knowledge
        # self.insert_knowledge()

    def insert_knowledge(self, **kwargs) -> None:
        """
        Load criminal law pdf and save into vector database.
        """
        criminal_law_docs = self.reader.load_data(Path("../resources/刑法.pdf"))
        lc_doc_list = SPLITTER.split_documents(Document.as_langchain_list(
            criminal_law_docs
        ))
        self.store.insert_documents(Document.from_langchain_list(lc_doc_list))
