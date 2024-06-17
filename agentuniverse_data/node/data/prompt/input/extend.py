# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 17:30
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: extend.py
import json
import math

from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_data.node.data.base.prompt_base import PromptBase
from agentuniverse.base.util.logging.logging_util import LOGGER


class ExtendNode(PromptBase):
    """The ExtendNode class, which is used to define the class of extend node."""

    extend_times: int = 4

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        self.extend_times = self._get_node_param('extend_times')

    def _node_process(self) -> None:
        if not self._prompt_list or len(self._prompt_list) == 0:
            return
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)
        prompt_with_extend_times = version_prompt.prompt_template.replace('<extend_times>', str(self.extend_times))

        input_list = ''
        input_len = len(self._prompt_list)
        inputs = self._prompt_list
        prompts = []
        batch_size = math.ceil(20 / self.extend_times)
        for i in range(0, input_len):
            input_list = input_list + inputs[i] + '\n'
            if (i + 1) % batch_size == 0 or i == input_len - 1:
                prompts.append(prompt_with_extend_times.replace('<input_list>', input_list))
                input_list = ''

        llm = LLMManager().get_instance_obj(self.llm)
        responses = llm.batch_call(prompts)

        for i in range(0, len(responses)):
            try:
                if responses[i] != '' and responses[i] is not None:
                    data = json.loads(responses[i])
                    if 'extend_inputs' in data:
                        extend_inputs = data['extend_inputs']
                        self._prompt_list.extend(extend_inputs)
            except Exception as e:
                LOGGER.warn(f'except[]>>>{e}:{responses[i]}')
                continue
