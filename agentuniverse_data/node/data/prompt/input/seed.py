# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 17:45
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: seed.py
import json

from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_data.node.data.base.prompt_base import PromptBase
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse_data.util.llm.llm_call import batch_call


class SeedNode(PromptBase):
    """The SeedNode class, which is used to define the class of seed node."""

    seeds_num: int = 100
    seed_gen_requirement: str = "金融领域"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'seeds_num' in kwargs:
            self.seeds_num = kwargs['seeds_num']

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        seeds_num = self._get_node_param('seeds_num')
        if seeds_num:
            self.seeds_num = seeds_num
        seed_gen_requirement = self._get_node_param('seed_gen_requirement')
        if seed_gen_requirement:
            self.seed_gen_requirement = seed_gen_requirement

    def _node_process(self) -> None:
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)
        prompt_with_seed_requirement = version_prompt.prompt_template.replace('<seed_requirement>',
                                                                              self.seed_gen_requirement)
        prompts = []

        for i in range(0, self.seeds_num):
            if (i + 1) % self._batch_line_size == 0:
                prompt = prompt_with_seed_requirement.replace('<seeds_num>', str(self._batch_line_size))
                prompts.append(prompt)
            elif i == self.seeds_num - 1:
                left_num = (i + 1) % self._batch_line_size
                prompt = prompt_with_seed_requirement.replace('<seeds_num>', str(left_num))
                prompts.append(prompt)

        responses = batch_call(prompts, self.llm)

        self._prompt_list = []
        for i in range(0, len(responses)):
            try:
                seeds = json.loads(responses[i])['seeds']
                self._prompt_list.extend(seeds)
            except TypeError as e:
                continue
            except json.decoder.JSONDecodeError as e:
                LOGGER.warn(f'except>>>{e}:{responses}')
                continue
