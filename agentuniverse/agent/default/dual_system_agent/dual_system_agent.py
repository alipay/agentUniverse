# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/1/22 16:00
# @Author  : [Your Name]
# @FileName: dual_system_agent.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from .constants import AgentKeys, SystemType
import json
import logging

class DualSystemAgent(Agent):
    """Dual System Agent class implementing fast and slow thinking."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return [AgentKeys.INPUT]

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return [AgentKeys.OUTPUT, AgentKeys.SYSTEM_TYPE, AgentKeys.CONFIDENCE]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing."""
        agent_input[AgentKeys.INPUT] = input_object.get_data(AgentKeys.INPUT)
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser."""
        # Extract the system type and confidence from planner result
        system_type: SystemType = planner_result.get(AgentKeys.SYSTEM_TYPE, 'slow')
        confidence = planner_result.get(AgentKeys.CONFIDENCE, 0.0)
        logging.debug(f"planner_result: {json.dumps(planner_result, ensure_ascii=False)}")
        return {
                AgentKeys.OUTPUT: planner_result.get(AgentKeys.OUTPUT),
                AgentKeys.SYSTEM_TYPE: system_type,
                AgentKeys.CONFIDENCE: confidence
            }
            

