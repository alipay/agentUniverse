# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/12 19:56
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: law_rag_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class LawRagAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result
