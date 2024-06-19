# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 15:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: seed.py
from langchain.output_parsers.json import parse_json_markdown

from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_data.node.data.base.prompt_base import PromptBase
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse_data.util.llm.llm_call import batch_call


class SeedNode(PromptBase):
    """The SeedNode class, which is used to define the class of extend node."""

    extend_times: int = 20

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        self.extend_times = self._get_node_param('extend_times')

    def _node_process(self) -> None:
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)
        prompt_with_extend_times = version_prompt.prompt_template.replace('<extend_times>',
                                                                          str(self.extend_times))

        prompts = [prompt_with_extend_times]
        responses = batch_call(prompts, self.llm)
        self._prompt_list = []
        if len(responses) == 1:
            try:
                if responses[0] != '' and responses[0] is not None:
                    data = parse_json_markdown(responses[0])
                    if 'instructs' in data:
                        extend_instructs = data['instructs']
                        self._prompt_list.extend(extend_instructs)
            except Exception as e:
                LOGGER.warn(f'except[]>>>{e}:{responses[0]}')
