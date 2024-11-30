# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/1/22 16:00
# @Author  : [Your Name]
# @FileName: dual_system_agent.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
import json

class DualSystemAgent(Agent):
    """Dual System Agent class implementing fast and slow thinking."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output', 'system_type', 'confidence']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result (dict): Planner result
        Returns:
            dict: Agent result object containing the system type (fast/slow),
                 confidence score, and output.
        """
        # Extract the system type and confidence from planner result
        system_type = planner_result.get('system_type', 'slow')
        confidence = planner_result.get('confidence', 0.0)
        
        if system_type == 'fast':
            # For fast thinking, return direct output
            return {
                "output": planner_result.get('result'),
                "system_type": "fast",
                "confidence": confidence
            }
        else:
            # For slow thinking, process through PEER framework
            peer_result = planner_result.get('result')
            print(f"Peer result: {json.dumps(peer_result, ensure_ascii=False)}")
            return {
                "output": peer_result,
                "system_type": "slow",
                "confidence": planner_result.get('confidence', 0.0)
            }
