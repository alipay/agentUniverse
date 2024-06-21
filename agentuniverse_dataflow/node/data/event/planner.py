# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/16 19:26
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: planner.py
import json
from typing import List, Dict

from langchain.output_parsers.json import parse_json_markdown

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse_dataflow.util.fileio.node_msg_jsonl import JsonFileReader
from agentuniverse_dataflow.node.enum.enum import NodeEnum
from agentuniverse_dataflow.node.base.data_node_base import DataNodeBase
from agentuniverse_dataflow.util.llm.llm_call import batch_call


class PlannerNode(DataNodeBase):
    """The PlannerNode class, which is used to define the class of planner node."""

    _perceived_prompt_list: List[str] = []
    _perceived_answer_list: List[str] = []
    _perceived_list_size: int = 0

    _new_plan_dict: Dict = {}
    _last_plan_dict: Dict = None
    _verify_lines: int = None

    def __init__(self, *args, **kwargs):
        super().__init__(node_type=NodeEnum.PROMPT_ANSWER)

    def _node_preprocess(self) -> None:
        super()._node_preprocess()
        self._verify_lines = int(self._get_node_param('verify_lines'))
        if self._dataset_in_handler:
            perceived_list = self._dataset_in_handler.read_json_obj_list()
            # one for plan , at least one for verification
            if not perceived_list or len(perceived_list) < 1:
                raise Exception('perceived json list does not provide at least 1 samples!')

            for i in range(0, len(perceived_list)):
                json_obj = perceived_list[i]
                self._perceived_prompt_list.append(json_obj['prompt'])
                self._perceived_answer_list.append(json_obj['answer'])
                self._perceived_list_size += 1

        if self.param_out_jsonl:
            jr = JsonFileReader(self.param_out_jsonl)
            self._last_plan_dict = jr.read_json_obj()
        if self._param_in_handler:
            self._new_plan_dict.update(self._param_in_handler.read_json_obj())

        self._new_plan_dict['prompt_plan'] = {
            'input_var': 'input_str',
            'output_var': 'prompt',
            'plan_code': None
        }
        self._new_plan_dict['answer_plan'] = {
            'input_var': 'input_str',
            'output_var': 'answer',
            'plan_code': None
        }

    def _node_process(self) -> None:
        # check whether last plan works or not
        if self.__check_last_plan():
            self._new_plan_dict = self._last_plan_dict
            return

        prompt_plan_code = self.__generate_plan_and_verify(self._new_plan_dict.get('prompt_plan'),
                                                           self._perceived_prompt_list)
        answer_plan_code = self.__generate_plan_and_verify(self._new_plan_dict.get('answer_plan'),
                                                           self._perceived_answer_list)
        if prompt_plan_code and answer_plan_code:
            self._new_plan_dict['prompt_plan']['plan_code'] = prompt_plan_code
            self._new_plan_dict['answer_plan']['plan_code'] = answer_plan_code

    def __check_last_plan(self) -> bool:
        if not self._last_plan_dict:
            return False

        last_plan = self._last_plan_dict.get('prompt_plan')
        last_plan_code = last_plan.get('plan_code')
        last_output_var = last_plan.get('output_var')
        dict_obj = self.execute_from_plan(self._perceived_prompt_list, 0, 1, last_plan_code, last_output_var)
        if dict_obj.get('reflection'):
            return False

        last_plan = self._last_plan_dict.get('answer_plan')
        last_plan_code = last_plan.get('plan_code')
        last_output_var = last_plan.get('output_var')
        dict_obj = self.execute_from_plan(self._perceived_answer_list, 0, 1, last_plan_code, last_output_var)
        if dict_obj.get('reflection'):
            return False

        return True

    def __generate_plan_and_verify(self, plan_list: str, data_list: list) -> str:

        output_var = plan_list.get('output_var')
        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)

        prompt_template = getattr(version_prompt, 'data_event_plan', '').replace('<output_var>', output_var)
        prompt_reflection_template = prompt_template.replace('<input_str>', data_list[0])
        prompt = prompt_reflection_template.replace('<reflection>', 'None')

        llm_retry = 10
        reflection_retry = 10
        last_reflection = None
        while True:
            if llm_retry <= 0 or reflection_retry <= 0:
                return None

            LOGGER.debug(prompt)
            res = batch_call([prompt], self.llm)
            LOGGER.debug(res)

            try:
                res_obj = parse_json_markdown(res[0].strip())
                LOGGER.debug(res_obj)
            except json.decoder.JSONDecodeError as e:
                reflection = 'exception: ' + str(e) + '\ncode: json.loads'
                if reflection == last_reflection:
                    reflection = 'None'
                prompt = prompt_reflection_template.replace('<reflection>', reflection)
                last_reflection = reflection
                LOGGER.warn(e)
                continue

            plan_code = res_obj["plan_code"].strip()
            LOGGER.debug(f'plan_code>>>{plan_code}')

            reflection_retry -= 1
            start_idx = 1
            verify_lines = 10 if not self._verify_lines else self._verify_lines
            if verify_lines > self._perceived_list_size - start_idx:
                verify_lines = self._perceived_list_size - start_idx

            dict_obj = self.execute_from_plan(data_list, start_idx, verify_lines, plan_code, output_var)
            reflection = dict_obj.get('reflection')
            LOGGER.debug(f'reflection:{reflection}')

            if reflection:
                if reflection == last_reflection:
                    reflection = 'None'
                prompt = prompt_reflection_template.replace('<reflection>', reflection)
                last_reflection = reflection
            else:
                return plan_code

        return None

    def _node_postprocess(self) -> None:
        super()._node_postprocess()

        if self._param_out_handler:
            self._param_out_handler.write_json_obj(self._new_plan_dict)

    def check_data_reflection(self, data_str: str) -> str:
        if not data_str or data_str == '':
            return 'Output cannot be empty'

        version_prompt: Prompt = PromptManager().get_instance_obj(self.prompt_version)

        prompt = getattr(version_prompt, 'exec_result_verification', '').replace('<input_lines>', data_str)
        LOGGER.debug(prompt)
        res = batch_call([prompt], self.llm)
        LOGGER.debug(res[0])
        json_obj = parse_json_markdown(res[0])
        if json_obj.get('success'):
            return None
        else:
            return json_obj.get('reflection')

    def execute_from_plan(self, data_list: list, start_idx: int, execute_lines: int, plan_code: str,
                          output_var: str) -> Dict:
        reflection = None
        output_list = []
        for i in range(start_idx, start_idx + execute_lines):
            namespace = {
                'input_str': data_list[i],
                output_var: '',
            }

            try:
                exec(plan_code, globals(), namespace)
            except Exception as e:
                LOGGER.warn(f'except from exec>>>{e}')
                reflection = 'exec Exception:' + str(e) + '\ncode:' + plan_code
                break

            output = namespace.get(output_var)
            LOGGER.debug(f'after exec >>>{output}')

            if output == '':
                reflection = "The output is empty"
                break
            if not isinstance(output, str):
                reflection = 'The type of output must be a string，the current output type is: ' + str(
                    type(output)) + ', the original code is as follows: ' + plan_code
                break

            result_str = output_var + ':' + output
            reflection = self.check_data_reflection(result_str)
            if reflection:
                break
            else:
                output_list.append(output)

        return {'reflection': reflection, 'output_list': output_list}
