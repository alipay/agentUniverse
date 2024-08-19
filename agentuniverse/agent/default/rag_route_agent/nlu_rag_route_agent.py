# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/13 11:20
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: nlu_rag_route_agent.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class NluRagRouteAgent(Agent):
    """Rag Agent class."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['query', 'store_info', 'store_amount']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        agent_input['query'] = input_object.get_data('query')
        agent_input['store_info'] = input_object.get_data('store_info')
        agent_input['store_amount'] = input_object.get_data('store_amount')
        self.agent_model.profile.setdefault('prompt_version',
                                            'nlu_rag_route_prompt.cn')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        return planner_result
