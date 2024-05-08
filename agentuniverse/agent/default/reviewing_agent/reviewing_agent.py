# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/19 20:03
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: reviewing_agent.py
"""Reviewing Agent class."""
import json
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class ReviewingAgent(Agent):
    """Reviewing Agent module."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input', 'expressing_result']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, planner_input: dict) -> dict:
        """Planner parameter parsing.

        Args:
            input_object(InputObject): agent parameter object
            planner_input(dict): Planner input
        Returns:
            dict: Planner parameter.
        """
        planner_input['input'] = input_object.get_data('input')
        planner_input['expressing_result'] = input_object.get_data('expressing_result').get_data('output')
        self.agent_model.profile.setdefault('prompt_version', 'default_reviewing_agent.cn')
        return planner_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        agent_result = dict()

        output = planner_result.get('output')
        output = json.loads(output)
        is_useful = output.get('is_useful')
        if is_useful is None:
            is_useful = False
        is_useful = bool(is_useful)
        if is_useful:
            score = 80
        else:
            score = 0

        agent_result['output'] = output
        agent_result['score'] = score
        agent_result['suggestion'] = output.get('suggestion')
        return agent_result
