#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/10 16:40
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：test_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER


class TestAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        # agent_input['chat_history'] = input_object.get_data('chat_history')
        # agent_input['input'] = {'chat_history': [{'content': '苹果', 'type': 'human'}, {'content': '你好，你提到的"苹果"通常指的是一种水果，营养丰富，口感脆甜。你想了解关于苹果的营养价值、如何挑选、食用方法还是想分享你的苹果经历？告诉我你的需求，我会尽力帮助你。', 'type': 'ai'}, {'content': '如何挑选', 'type': 'human'}], 'background': '', 'image_urls': [], 'date': '2024-07-11', 'input': '如何挑选'}
        LOGGER.debug(f"debug触发 parse_input agent_input {agent_input}")
        LOGGER.debug(f"debug触发 parse_input input {input_object.get_data('input')}")
        LOGGER.debug(f"debug触发 parse_input chat_history {input_object.get_data('chat_history')}")
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        LOGGER.debug(f"触发 parse_result agent_input {planner_result}")
        return planner_result
