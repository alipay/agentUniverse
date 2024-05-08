# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 19:28
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_knowledge.py

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
