# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/19 19:37
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: expressing_agent.py
"""Expressing Agent module."""
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class ExpressingAgent(Agent):
    """Expressing Agent class."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, planner_input: dict) -> dict:
        """Planner parameter parsing.

        Args:
            input_object(InputObject): agent parameter object
            planner_input(dict): Planner input
        Returns:
            dict: Planner input
        """
        planner_input['input'] = input_object.get_data('input')
        planner_input['background'] = self.build_background(input_object)
        self.agent_model.profile.setdefault('prompt_version', 'default_expressing_agent.cn')
        return planner_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        return planner_result

    def build_background(self, input_object: InputObject) -> str:
        """Build the background knowledge.

        Args:
            input_object(InputObject): agent parameter object
        Returns:
            str: Background knowledge.
        """
        executing_result = input_object.get_data('executing_result').get_data('executing_result', [])
        knowledge_list = []
        for execution in executing_result:
            knowledge_list.append("question:" + execution.get('input'))
            knowledge_list.append("answer:" + execution.get('output'))

        return '\n\n'.join(knowledge_list)
