# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from langchain_text_splitters import RecursiveCharacterTextSplitter

# @Time    : 2024/6/25 16:56
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: translation_planner.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class TranslationAgent(Agent):
    def input_keys(self) -> list[str]:
        return self.agent_model.profile.get('input_keys')

    def output_keys(self) -> list[str]:
        return self.agent_model.profile.get('output_keys')

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in self.input_keys():
            agent_input[key] = input_object.get_data(key)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        return planner_result
