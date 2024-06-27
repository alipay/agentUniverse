# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/16 19:25
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: perceiver.py
from typing import List, Dict

from agentuniverse_dataflow.node.enum.enum import NodeEnum
from agentuniverse_dataflow.node.base.data_node_base import DataNodeBase
from agentuniverse_dataflow.util.fileio.node_msg_jsonl import JsonFileReader
from agentuniverse.base.util.logging.logging_util import LOGGER


class PerceiverNode(DataNodeBase):
    """The PerceiverNode class, which is used to define the class of perceiver node."""

    event_db: str = None
    event_uri: str = None
    event_sql: str = None
    prompt_col: str = None
    answer_col: str = None

    _input_data_jsonlist: List[Dict] = None

    def __init__(self, *args, **kwargs):
        super().__init__(node_type=NodeEnum.PROMPT_ANSWER)

    def _node_preprocess(self) -> None:
        LOGGER.info("------------------------------------------------------------------------------------")
        LOGGER.info("PerceiverNode preprocess start: read PerceiverNode configuration from auto_event.yaml")
        super()._node_preprocess()

        self.event_db = self._get_node_param('event_db')
        self.event_uri = self._get_node_param('event_uri')
        self.event_sql = self._get_node_param('event_sql')
        self.prompt_col = self._get_node_param('prompt_col')
        self.answer_col = self._get_node_param('answer_col')

    def _node_process(self) -> None:
        LOGGER.info("PerceiverNode process start: read the dataset from the user-configured jsonl file.")
        if self.event_db:
            if self.event_db == 'jsonl':
                self._input_data_jsonlist = JsonFileReader(self.event_uri).read_json_obj_list()

    def _node_postprocess(self) -> None:
        LOGGER.info("PerceiverNode postprocess start: assemble the raw input and output from the dataset into "
                     "the dictionary dataset with 'prompt' and 'answer' keys.")
        super()._node_postprocess()
        if self._input_data_jsonlist is not None and self._dataset_out_handler:
            for i in range(0, len(self._input_data_jsonlist)):
                prompt_related_str = self._input_data_jsonlist[i].get(self.prompt_col)
                answer_related_str = self._input_data_jsonlist[i].get(self.answer_col)

                self._dataset_out_handler.write_json_prompt_answer(prompt_related_str, answer_related_str)

        if self._param_out_handler:
            param_obj = {
                'event_db': self.event_db,
                'event_uri': self.event_uri,
                'event_sql': self.event_sql,
                'prompt_col': self.prompt_col,
                'answer_col': self.answer_col
            }
            self._param_out_handler.write_json_obj(param_obj)
