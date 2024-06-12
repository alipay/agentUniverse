import json
from typing import Any, Union, AsyncIterator, Iterator, Optional, List, Sequence

import tiktoken
from langchain_community.llms.ollama import _OllamaCommon
from langchain_core.language_models import BaseLanguageModel
from ollama import Options

from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.ollama_langchain_instance import OllamaLangchainInstance


class OllamaLLM(LLM):
    base_url: str = "http://localhost:11434"
    """Base url the model is hosted under."""

    streaming: bool = True

    def _new_client(self):
        if self.client:
            return self.client
        from ollama import Client
        return Client(
            host=self.base_url,
        )

    def _new_async_client(self):
        if self.async_client:
            return self.async_client
        from ollama import AsyncClient
        return AsyncClient(
            host=self.base_url,
        )

    def _options(self):
        return Options(**{
            "num_ctx": self.max_context_length(),
            "num_predict": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.request_timeout,
            **(self.ext_info if self.ext_info else {}),
        })

    def call(self, messages, stop=None, **kwargs) -> Union[LLMOutput, Iterator[LLMOutput]]:
        client = self._new_client()
        res = client.chat(model=self.model_name, messages=messages, options=self._options(), stream=self.streaming)
        for line in res:
            yield LLMOutput(text=line.get("message").get('content'), raw=json.dumps(line))

    async def acall(self, messages, stop=None, **kwargs) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        client = self._new_async_client()
        res = client.chat(model=self.model_name, messages=messages, options=self.options, stream=self.streaming)
        async for line in res:
            yield LLMOutput(text=line.get("message").get('content'), raw=json.dumps(line))

    def as_langchain(self) -> BaseLanguageModel:
        return OllamaLangchainInstance(
            self
        )

    def get_num_tokens(self, text: str) -> int:
        encoding = tiktoken.encoding_name_for_model(self.model_name)
        return encoding.count(text)


if __name__ == '__main__':
    llm = OllamaLLM(
        base_url="http://localhost:11434",
        model_name="qwen2:7b",
    )
    # res = llm.call(messages=[{
    #     "role": "user",
    #     "content": "你好"
    # }])
    # for data in res:
    #     print(data)
    langchain_llm = llm.as_langchain()
    res = langchain_llm.invoke(input='请问你是谁')
    print(res)
