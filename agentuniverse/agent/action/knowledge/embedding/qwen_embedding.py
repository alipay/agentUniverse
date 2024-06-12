# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/11 16:30
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: qwen_embedding.py


from typing import List, Optional

import dashscope
from langchain_community.embeddings import DashScopeEmbeddings
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env


class QwenEmbedding(Embedding):
    """The openai embedding class."""

    dashscope_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_API_KEY"))
    """The DashScope client."""
    model: Optional[str] = "text-embedding-v1"

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get the OpenAI embeddings.

        Note:
            The `embedding_model_name` parameter of the openai embedding class must be provided.
            The `dimensions` parameter of the openai embedding class is optional.

         Args:
             texts (List[str]): A list of texts that need to be embedded.

         Returns:
             List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.

         Raises:
             ValueError: If texts exceed the embedding model token limit or missing some required parameters.
         """
        result = []
        resp = dashscope.TextEmbedding.call(
            model=self.model,
            input=texts,
            api_key=self.dashscope_api_key
        )
        if resp.status_code == 200:
            result = [item['embedding'] for item in resp.output.get('embeddings')]
        elif resp.status_code in [400, 401]:
            raise ValueError(
                f"status_code: {resp.status_code} \n "
                f"code: {resp.code} \n message: {resp.message}"
            )
        else:
            raise Exception(f"status_code: {resp.status_code} \n code: {resp.code} \n message: {resp.message}")
        return result

    async def async_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get the OpenAI embeddings.

        Note:
            The `embedding_model_name` parameter of the openai embedding class must be provided.
            The `dimensions` parameter of the openai embedding class is optional.

         Args:
             texts (List[str]): A list of texts that need to be embedded.

         Returns:
             List[List[float]]: Each text gets a float list, and the result is a list of the results for each text.
         Raises:
             ValueError: If texts exceed the embedding model token limit or missing some required parameters.
         """
        raise NotImplementedError

    def as_langchain(self) -> DashScopeEmbeddings:
        """Convert the agentUniverse(aU) openai embedding class to the langchain openai embedding class."""
        return DashScopeEmbeddings(
            model=self.model,
            dashscope_api_key=self.dashscope_api_key,
        )
