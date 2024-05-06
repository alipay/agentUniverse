# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/19 11:43
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_embedding.py
from typing import List, Optional, Any

from langchain_community.embeddings.openai import OpenAIEmbeddings
from openai import OpenAI, AsyncOpenAI, BadRequestError
from pydantic import Field

from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding
from agentuniverse.base.util.env_util import get_from_env


class OpenAIEmbedding(Embedding):
    """The openai embedding class."""

    openai_client_args: Optional[dict] = None
    openai_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_API_KEY"))
    client: Any = None
    async_client: Any = None
    dimensions: Optional[int] = None

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
        self.client = OpenAI(api_key=self.openai_api_key, **self.openai_client_args or {})
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        try:
            if self.dimensions:
                response = self.client.embeddings.create(input=texts, model=self.embedding_model_name,
                                                         dimensions=self.dimensions)
            else:
                response = self.client.embeddings.create(input=texts, model=self.embedding_model_name)

            # Extract the embedding data from the response
            data = response.data

            # Return the embeddings as a list of lists of floats
            return [embedding.embedding for embedding in data]
        except BadRequestError as e:
            raise ValueError(e.message)

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
        self.async_client = AsyncOpenAI(api_key=self.openai_api_key, **self.openai_client_args or {})
        if self.embedding_model_name is None:
            raise ValueError("Must provide `embedding_model_name`")
        try:
            if self.dimensions:
                response = await self.async_client.embeddings.create(input=texts, model=self.embedding_model_name,
                                                                     dimensions=self.dimensions)
            else:
                response = await self.async_client.embeddings.create(input=texts, model=self.embedding_model_name)
            # Extract the embedding data from the response
            data = response.data

            # Return the embeddings as a list of lists of floats
            return [embedding.embedding for embedding in data]
        except BadRequestError as e:
            raise ValueError(e.message)

    def as_langchain(self) -> OpenAIEmbeddings:
        """Convert the AgentUniverse(AU) openai embedding class to the langchain openai embedding class."""
        return OpenAIEmbeddings(openai_api_key=self.openai_api_key,
                                client=self.client.embeddings, async_client=self.async_client.embeddings)
