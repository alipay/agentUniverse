# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: baichuan_openai_style_llm.py

from typing import Optional

from langchain_community.chat_models import ChatBaichuan
from langchain_core.language_models import BaseLanguageModel
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

BAICHUAN_Max_CONTEXT_LENGTH = {
    "Baichuan2-53B": 8000,
    "Baichuan2-Turbo": 8000,
    "Baichuan2-192K": 192000
}


class BAICHUANOpenAIStyleLLM(OpenAIStyleLLM):
    """
    BAICHUAN OpenAI Style LLM
    Args:
        api_key (Optional[str]): API key for the model. Defaults to None.
        api_base (Optional[str]): API base URL for the model. Defaults to "https://api.openai.com/v1".
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("BAICHUAN_API_KEY"))
    api_base: Optional[str] = "https://api.baichuan-ai.com/v1"

    def max_context_length(self) -> int:
        if self.model_max_context_length:
            return self.model_max_context_length
        return BAICHUAN_Max_CONTEXT_LENGTH.get(self.model_name, 8000)

    def as_langchain(self) -> BaseLanguageModel:
        llm = self
        init_params = dict()
        init_params['model'] = llm.model_name if llm.model_name else 'Baichuan2-Turbo'
        init_params['temperature'] = llm.temperature if llm.temperature else 0.7
        init_params['request_timeout'] = llm.request_timeout
        init_params['streaming'] = llm.streaming if llm.streaming else False
        init_params['baichuan_api_key'] = llm.api_key if llm.api_key else 'blank'
        init_params['timeout'] = llm.timeout if llm.request_timeout else 60
        init_params['model_kwargs'] = {
            'max_tokens': llm.max_tokens,
            'max_retries': llm.max_retries if llm.max_retries else 2,
        }
        return ChatBaichuan(
            **init_params
        )
