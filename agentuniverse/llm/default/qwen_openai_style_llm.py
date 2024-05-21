# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: qwen_openai_style_llm.py

from typing import Optional

from dashscope import get_tokenizer
from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

QWen_Max_CONTEXT_LENGTH = {
    "qwen-turbo": 6000,
    "qwen-plus": 300000,
    "qwen-max": 6000,
    "qwen-max-0428": 6000,
    "qwen-max-0403": 6000,
    "qwen-max-0107": 6000,
    "qwen-max-longcontext": 28000
}


class QWenOpenAIStyleLLM(OpenAIStyleLLM):

    """
        QWen OpenAI style LLM
        Args:
            api_key: API key for the model ,from dashscope : DASHSCOPE_API_KEY
            api_base: API base URL for the model, from dashscope : DASHSCOPE_API_BASE
    """

    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_API_KEY"))
    api_base: Optional[str] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def max_context_length(self) -> int:
        if self.model_max_context_length:
            return self.model_max_context_length
        return QWen_Max_CONTEXT_LENGTH.get(self.model_name, 8000)

    def get_num_tokens(self, text: str) -> int:
        tokenizer = get_tokenizer(self.model_name)
        return len(tokenizer.encode(text))
