# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/12/12 20:58
# @Author  : jijiawei
# @Email   : jijiawei.jjw@antgroup.com
# @FileName: pet_insurance_rewrite_agent.py
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.template.rag_agent_template import RagAgentTemplate
from agentuniverse.base.util.logging.logging_util import LOGGER


class PetInsuranceRewriteAgent(RagAgentTemplate):
    def input_keys(self) -> list[str]:
        return ['input', 'prod_description']

    def output_keys(self) -> list[str]:
        return ['rewrite_output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        agent_input['prod_description'] = input_object.get_data('prod_description')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        rewrite_output = agent_result['output']
        LOGGER.info(f'智能体 pet_question_planning_agent 执行结果为： {rewrite_output}')
        return {**agent_result, 'rewrite_output': agent_result['output']}