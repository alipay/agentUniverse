# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/6 22:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: host_agent.py
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class HostAgent(Agent):

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object(InputObject): input parameters passed by the user.
            agent_input(dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['participants'] = input_object.get_data('participants')
        agent_input['total_round'] = input_object.get_data('total_round')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        return planner_result
