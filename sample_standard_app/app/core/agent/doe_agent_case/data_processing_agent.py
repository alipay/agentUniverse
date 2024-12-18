# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/18 15:25
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: data_processing_agent.py

from langchain_core.utils.json import parse_json_markdown

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class DataProcessingAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input','init_data']

    def output_keys(self) -> list[str]:
        return ['data_processing_result']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in input_object.to_dict():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return {
            'data_processing_result': parse_json_markdown(planner_result.get('output'))
        }
