# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:20
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: default_openai_llm.py
from typing import Any

from agentuniverse.llm.llm_output import LLMOutput
from agentuniverse.llm.openai_llm import OpenAILLM


class DefaultOpenAILLM(OpenAILLM):
    """The agentUniverse default openai llm module.

    LLM parameters, such as name/description/model_name/max_tokens,
    are injected into this class by the default_openai_llm.yaml configuration.
    """

    def call(self, messages: list, **kwargs: Any) -> LLMOutput:
        """ The call method of the LLM.

        Users can customize how the model interacts by overriding call method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return super().call(messages, **kwargs)

    async def acall(self, messages: list, **kwargs: Any) -> LLMOutput:
        """ The async call method of the LLM.

        Users can customize how the model interacts by overriding acall method of the LLM class.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        return await super().acall(messages, **kwargs)
