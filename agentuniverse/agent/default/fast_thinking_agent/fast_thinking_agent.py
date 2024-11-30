# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/1/22 17:00
# @Author  : [Your Name]
# @FileName: fast_thinking_agent.py

"""Fast thinking agent module for System 1 processing."""
from langchain.output_parsers.json import parse_json_markdown

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.common.constants import AgentKeys
from agentuniverse.agent.default.dual_system_agent.constants import (DualSystemKeys)


class FastThinkingAgent(Agent):
    """Fast Thinking Agent class for System 1."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return [AgentKeys.INPUT]

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return [AgentKeys.OUTPUT, DualSystemKeys.CONFIDENCE, DualSystemKeys.THOUGHT]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing."""
        agent_input[AgentKeys.INPUT] = input_object.get_data(AgentKeys.INPUT)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser."""
        output = planner_result.get(AgentKeys.OUTPUT)
        output = parse_json_markdown(output)
        return {
            AgentKeys.OUTPUT: output.get(DualSystemKeys.RESPONSE),
            DualSystemKeys.CONFIDENCE: output.get(DualSystemKeys.CONFIDENCE, 0.0),
            DualSystemKeys.THOUGHT: output.get(DualSystemKeys.THOUGHT, '')
        }
