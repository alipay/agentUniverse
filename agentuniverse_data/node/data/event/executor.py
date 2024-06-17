# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/16 19:22
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: executor.py
from typing import List, Tuple, Dict

import pandas as pd

from agentuniverse_data.node.enum.enum import NodeEnum
from agentuniverse_data.node.base.data_node_base import DataNodeBase
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse_data.util.fileio.node_msg_jsonl import JsonFileReader


class ExecutorNode(DataNodeBase):
    """The ExecutorNode class, which is used to define the class of executor node."""

    event_db: str = None
    event_uri: str = None
    event_sql: str = None
    prompt_col: str = None
    answer_col: str = None

    _data_frame: pd.DataFrame = None
    _plan_dict: Dict = None
    _input_data_jsonlist: List[Dict] = None
    _dump_prompt_answer_list: List[Tuple[str, str]] = []

    def __init__(self, *args, **kwargs):
        super().__init__(node_type=NodeEnum.PROMPT_ANSWER)

    def _node_preprocess(self) -> None:
        super()._node_preprocess()
        if self._param_in_handler:
            self._plan_dict = self._param_in_handler.read_json_obj()

            self.event_db = self._plan_dict.get('event_db')
            self.event_uri = self._plan_dict.get('event_uri')
            self.event_sql = self._plan_dict.get('event_sql')
            self.prompt_col = self._plan_dict.get('prompt_col')
            self.answer_col = self._plan_dict.get('answer_col')

    def _node_process(self) -> None:
        if self.event_db:
            if self.event_db == 'jsonl':
                self._input_data_jsonlist = JsonFileReader(self.event_uri).read_json_obj_list()
                self.__dump_from_plan()

    def __dump_from_plan(self):
        prompt_plan_code = self._plan_dict.get('prompt_plan').get('plan_code')
        answer_plan_code = self._plan_dict.get('answer_plan').get('plan_code')
        prompt_input_var = self._plan_dict.get('prompt_plan').get('input_var')
        answer_input_var = self._plan_dict.get('answer_plan').get('input_var')
        prompt_output_var = self._plan_dict.get('prompt_plan').get('output_var')
        answer_output_var = self._plan_dict.get('answer_plan').get('output_var')

        for i in range(0, len(self._input_data_jsonlist)):
            prompt_related_str = self._input_data_jsonlist[i].get(self.prompt_col)
            answer_related_str = self._input_data_jsonlist[i].get(self.answer_col)

            prompt_namespace = {
                prompt_input_var: prompt_related_str,
                prompt_output_var: ''
            }
            answer_namespace = {
                answer_input_var: answer_related_str,
                answer_output_var: ''
            }

            try:
                exec(prompt_plan_code, globals(), prompt_namespace)
                exec(answer_plan_code, globals(), answer_namespace)
            except Exception as e:
                LOGGER.warn(
                    f'exception from exec>>>{e}:\nprompt_plan_code:{prompt_plan_code}\nanswer_plan_code:{answer_plan_code}')
                break

            prompt = prompt_namespace.get(prompt_output_var)
            answer = answer_namespace.get(answer_output_var)
            self._dump_prompt_answer_list.append((prompt, answer))

            if self._dataset_out_handler:
                self._dataset_out_handler.write_json_prompt_answer_list(self._dump_prompt_answer_list)
                self._dump_prompt_answer_list.clear()

    def _node_postprocess(self) -> None:
        super()._node_postprocess()
