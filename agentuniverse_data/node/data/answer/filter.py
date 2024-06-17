# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 14:46
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: filter.py
import json

from langchain.output_parsers.json import parse_json_markdown

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_data.node.data.base.prompt_answer_base import PromptAnswerBase
from agentuniverse_data.util.fileio.node_msg_jsonl import JsonFileReader, JsonFileWriter


class FilterNode(PromptAnswerBase):
    """The FilterNode class, which is used to define the class of filter node."""

    dimscore_threshold: int = 70
    avgscore_threshold: int = 70

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        self.dimscore_threshold = self._get_node_param('dimscore_threshold')
        self.avgscore_threshold = self._get_node_param('avgscore_threshold')

    def _node_process(self) -> None:
        if not self._prompt_answer_list or len(self._prompt_answer_list) == 0:
            return

        self.__quality_eval()
        self.__filter_items()

    def __quality_eval(self) -> None:
        prompts = []
        total_lines = 0
        jfw_quality = JsonFileWriter(self.dataset_out_jsonl + '.eval')

        list_len = len(self._prompt_answer_list)
        for i in range(0, list_len):
            do_req = False
            prompt = self._prompt_answer_list[i][0]
            answer = self._prompt_answer_list[i][1]
            total_lines += 1

            if not prompt or not answer:
                continue

            prompts.append(self.generate_prompt(prompt, answer))

            if total_lines % self._batch_prompt_size == 0:
                do_req = True
            elif i + 1 == list_len and len(prompts) > 0:
                do_req = True

            if do_req:
                llm = LLMManager().get_instance_obj(self.llm)
                res = llm.batch_call(prompts)

                start_line_num = total_lines - len(prompts)
                for res_idx in range(0, len(res)):
                    try:
                        if res[res_idx] and res[res_idx] != '':
                            json_obj = parse_json_markdown(str(res[res_idx]))
                            json_obj['line'] = start_line_num + res_idx + 1
                            jfw_quality.write_json_obj(json_obj)
                    except json.JSONDecodeError as e:
                        LOGGER.warn(f'except[__quality_eval]>>>{e}:{res[res_idx]}')
                prompts = []

    def __filter_items(self) -> None:
        jfr_quality = JsonFileReader(self.dataset_out_jsonl + '.eval')
        jfw_pos = JsonFileWriter(self.dataset_out_jsonl + '.pos')
        jfw_neg = JsonFileWriter(self.dataset_out_jsonl + '.neg')

        prompt_answer_list = self._prompt_answer_list
        self._prompt_answer_list = []

        while True:
            json_obj = jfr_quality.read_json_obj()
            if json_obj:
                dimensions = json_obj.get('dimensions')

                score_sum = 0.0
                is_pos = True
                for i in range(0, len(dimensions)):
                    score = float(dimensions[i].get('score'))
                    score_sum = score_sum + score
                    if score < self.dimscore_threshold:
                        is_pos = False

                avg_score = score_sum / len(dimensions)
                if avg_score < self.avgscore_threshold:
                    is_pos = False

                if is_pos:
                    jfw_pos.write_json_obj(json_obj)
                    if 'line' in json_obj:
                        line = json_obj['line']
                        if line > 0:
                            self._prompt_answer_list.append(prompt_answer_list[line - 1])
                else:
                    jfw_neg.write_json_obj(json_obj)

            else:
                break

    def generate_prompt(self, prompt_str: str, answer_str: str) -> str:
        if len(prompt_str) > 2000:
            prompt_str = prompt_str[0:2000]
        if len(answer_str) > 5000:
            answer = answer_str[0:5000]
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)

        prompt = version_prompt.prompt_template.replace("<prompt_str>", prompt_str)
        prompt = prompt.replace("<answer_str>", answer_str)

        return prompt
