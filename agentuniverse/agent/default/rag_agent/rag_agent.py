# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/25 15:03
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: rag_agent.py
"""Planning agent module."""
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class RagAgent(Agent):
    """Rag Agent class."""

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
        input = input_object.get_data('input')
        planner_input['input'] = input
        self.agent_model.profile.setdefault('prompt_version', 'default_rag_agent.cn')
        return planner_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        return planner_result
