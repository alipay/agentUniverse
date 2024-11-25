# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/1/22 17:00
# @Author  : [Your Name]
# @FileName: fast_thinking_agent.py

"""Fast thinking agent module for System 1 processing."""
from langchain.output_parsers.json import parse_json_markdown

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject


class FastThinkingAgent(Agent):
    """Fast Thinking Agent class for System 1."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output', 'confidence', 'thought']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        agent_input['input'] = input_object.get_data('input')
        # 设置快速思考的prompt模板
        self.agent_model.profile.setdefault('prompt_version', 'default_fast_thinking_agent.en')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result (dict): Planner result
        Returns:
            dict: Agent result object.
        """
        output = planner_result.get('output')
        output = parse_json_markdown(output)
        return {
            'output': output.get('response'),
            'confidence': output.get('confidence', 0.0),
            'thought': output.get('thought', '')
        }
