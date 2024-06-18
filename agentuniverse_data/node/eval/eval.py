# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 18:07
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: eval.py
from typing import List, Tuple

from langchain.output_parsers.json import parse_json_markdown

from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_data.node.base.eval_node_base import EvalNodeBase
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse_data.util.constant.eval_node_dimensions import get_eval_dims
from agentuniverse_data.util.llm.llm_call import batch_call


class EvalNode(EvalNodeBase):
    """The EvalNode class, which is used to define the class of eval node."""

    _prompt_answer_list: List[Tuple[str, str]] = None
    _eval_dims_json_list: List[str] = None
    _eval_lines: int = 100

    def set_eval_lines(self, eval_lines: int) -> None:
        if eval_lines > 0:
            self._eval_lines = eval_lines

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        self._eval_lines = self._get_node_param('eval_lines')
        if self._dataset_in_handler:
            self._prompt_answer_list = self._dataset_in_handler.read_json_prompt_answer_list()

    def _node_postprocess(self) -> None:
        super()._node_postprocess()

        if self._dataset_out_handler and self._eval_dims_json_list:
            self._dataset_out_handler.write_json_obj_list(self._eval_dims_json_list)

    def _node_process(self) -> None:
        if not self._prompt_answer_list or len(self._prompt_answer_list) == 0:
            return

        eval_dims = get_eval_dims()

        line_num = 0
        self._eval_dims_json_list = []
        for i in range(0, len(self._prompt_answer_list)):
            prompt = self._prompt_answer_list[i][0]
            answer = self._prompt_answer_list[i][1]

            if prompt is None:
                break

            line_num += 1
            if line_num > self._eval_lines:
                break

            if len(prompt) > 2000:
                prompt = prompt[0:2000]
            if len(answer) > 5000:
                answer = answer[0:5000]

            version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)

            eval_prompt_temp = version_prompt.prompt_template.replace('<prompt_str>', prompt)
            eval_prompt_temp = eval_prompt_temp.replace('<answer_str>', answer)
            eval_prompts = []

            for i in range(0, len(eval_dims)):
                eval_dim_name = eval_dims[i][0]
                eval_dim_requirement = eval_dims[i][1]
                eval_prompt = eval_prompt_temp.replace('<dim_name>', eval_dim_name)
                eval_prompt = eval_prompt.replace('<dim_requirement>', eval_dim_requirement)
                eval_prompts.append(eval_prompt)

            res = batch_call(eval_prompts, self.llm)

            dim_score_json = {'line': line_num}
            dimensions = []
            avg_score = 0.0
            for j in range(0, len(res)):
                try:
                    if res[j] != '' and res[j] is not None:
                        data = parse_json_markdown(res[j])
                        avg_score += data['score']
                        dimensions.append(data)
                except Exception as e:
                    LOGGER.warn(f'except[eval_prompt_answer_from_jsonl]>>>{e}:{res[j]}')
                    continue
            if len(res) > 0:
                avg_score = avg_score / len(res)
            dim_score_json['avg_score'] = avg_score
            dim_score_json['dimensions'] = dimensions

            self._eval_dims_json_list.append(dim_score_json)
