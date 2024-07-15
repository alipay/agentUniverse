#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/10 9:24
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：draft_contract_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER


class DraftContractAgent(Agent):
    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        LOGGER.debug(f"触发 parse_input agent_input {agent_input}")

        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        LOGGER.debug(f"触发 parse_result agent_input {planner_result}")
        return planner_result
