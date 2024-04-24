# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 19:18
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: embedding.py
from abc import abstractmethod
from typing import List, Optional

from pydantic import BaseModel
from langchain_core.embeddings import Embeddings as LCEmbeddings


class Embedding(BaseModel):
    """The basic class for embedding.

    Attributes:
        embedding_model_name (Optional[str]): The name of the embedding model.
    """

    embedding_model_name: Optional[str] = None

    @abstractmethod
    def get_embeddings(self, text: List[str]) -> List[List[float]]:
        """Get embeddings."""

    @abstractmethod
    async def async_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get embeddings."""

    def as_langchain(self) -> LCEmbeddings:
        """Convert the AgentUniverse(AU) embedding class to the langchain embedding class."""
        pass
