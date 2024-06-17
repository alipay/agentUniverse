# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 17:34
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: rewrite.py
import json

from langchain.output_parsers.json import parse_json_markdown

from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_data.node.data.base.prompt_base import PromptBase


class RewriteNode(PromptBase):
    """The RewriteNode class, which is used to define the class of rewrite node."""

    def _node_process(self) -> None:
        if not self._prompt_list or len(self._prompt_list) == 0:
            return

        prompts = []
        inputs = self._prompt_list
        inputs_all = ''
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)
        for i in range(0, len(inputs)):
            inputs_all = inputs_all + inputs[i] + '\n'
            if (i + 1) % self._batch_prompt_size == 0 or i == len(inputs) - 1:
                prompts.append(version_prompt.prompt_template.replace('<inputs>', inputs_all))
                inputs_all = ''

        llm = LLMManager().get_instance_obj(self.llm)
        responses = llm.batch_call(prompts)

        self._prompt_list = []
        for i in range(0, len(responses)):
            try:
                rewrite_input = parse_json_markdown(responses[i])['rewrite_inputs']
                self._prompt_list.extend(rewrite_input)
            except json.JSONDecodeError as e:
                # rewrite_inputs_all.extend(inputs)
                continue
