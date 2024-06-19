# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 14:57
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_gen.py
from typing import List

from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_dataflow.node.data.base.prompt_base import PromptBase
from agentuniverse_dataflow.util.fileio.node_msg_jsonl import JsonFileReader


class PromptGenNode(PromptBase):
    """The PromptGenNode class, which is used to define the class of prompt generate node."""

    _instruct_list: List[str] = None
    _input_sample: str = None

    _instruct_num: int = None

    def _node_preprocess(self) -> None:

        super()._node_preprocess()

        if not self.datasets_in_jsonl or len(self.datasets_in_jsonl) != 2:
            raise Exception(f"Node param {self.datasets_in_jsonl} should contain 2 elements:1.instruct 2.input")

        instruct_in_handler = JsonFileReader(self.datasets_in_jsonl[0])
        input_in_handler = JsonFileReader(self.datasets_in_jsonl[1])

        if instruct_in_handler:
            self._instruct_list = instruct_in_handler.read_json_prompt_list()
        if input_in_handler:
            self._input_sample = input_in_handler.read_json_prompt()

        self._instruct_num = self._get_node_param('instruct_num')

    def _node_process(self) -> None:

        self._prompt_list = []
        for instruct_idx in range(0, min(self._instruct_num, len(self._instruct_list))):
            prompt = self.generate_prompt_from_instruct_and_input(self._instruct_list[instruct_idx], self._input_sample)
            self._prompt_list.append(prompt)

    def generate_prompt_from_instruct_and_input(self, instruct='', input=''):
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)
        prompt = version_prompt.prompt_template.replace("<instruct>", instruct)
        prompt = prompt.replace("<input>", input)
        return prompt.strip()
