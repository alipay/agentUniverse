# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/1/22 16:30
# @Author  : [Your Name]
# @FileName: dual_system_planner.py

"""Dual System planner module implementing fast/slow thinking."""

from typing_extensions import sys
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import AgentManager, Planner
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.default.fast_thinking_agent.fast_thinking_agent import FastThinkingAgent
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.common.constants import AgentKeys
from agentuniverse.agent.default.dual_system_agent.constants import (
    DualSystemKeys, SystemType, ThinkingState, ThinkingResult
)


class DualSystemPlanner(Planner):
    """Dual system planner implementing System 1 (fast) and System 2 (slow) thinking."""
    
    def __init__(self) -> None:
        super().__init__()
        self._current_state = ThinkingState.EVALUATING
        self._confidence_threshold = 0.7  # Configurable threshold
        
    def _process_fast_thinking(self, agent_model: AgentModel, input_object: InputObject) -> ThinkingResult:
        """Process input using System 1 (fast thinking)."""
        system1_info = agent_model.plan.get('planner').get('system1')
        system1_agent_name = system1_info.get('name')
        self._confidence_threshold = system1_info.get('confidence_threshold')
        fast_agent = AgentManager().get_instance_obj(system1_agent_name)
        result = fast_agent.run(**input_object.to_dict())

        return ThinkingResult(
            system_type=SystemType.FAST,
            output=result.get_data(AgentKeys.OUTPUT),
            confidence=result.get_data(DualSystemKeys.CONFIDENCE, 0.0),
            thought=result.get_data(DualSystemKeys.THOUGHT)
        )
        
    def _process_slow_thinking(self, agent_model: AgentModel, input_object: InputObject) -> ThinkingResult:
        """Process input using System 2 (slow thinking)."""
        system2_agent_name = agent_model.plan.get('planner').get('system2').get('name')
        slow_agent = AgentManager().get_instance_obj(system2_agent_name)
        # mock = {
        #     AgentKeys.OUTPUT: "This is a mock response",
        #     DualSystemKeys.CONFIDENCE: 1.0,
        #     DualSystemKeys.THOUGHT: "System 2: This is the slow thinking process."
        # }
        # result = OutputObject(mock)
        result = slow_agent.run(**input_object.to_dict())
        return ThinkingResult(
            system_type=SystemType.SLOW,
            output=result.get_data(AgentKeys.OUTPUT),
            confidence=result.get_data(DualSystemKeys.CONFIDENCE, 0.0),
            thought=result.get_data(DualSystemKeys.THOUGHT)
        )

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner to process input using dual system thinking.
        
        Args:
            agent_model: The agent model to use
            planner_input: Additional planner parameters
            input_object: The input parameters
            
        Returns:
            dict: The final processing result
        """
        self._current_state = ThinkingState.EVALUATING
        
        # First try fast thinking (System 1)
        self._current_state = ThinkingState.FAST_PROCESSING
        fast_result = self._process_fast_thinking(agent_model, input_object)
        
        # If fast thinking is confident enough, return its result
        if fast_result.confidence >= self._confidence_threshold:
            self._current_state = ThinkingState.COMPLETED
            return fast_result.to_dict()
            
        # Otherwise, use slow thinking (System 2)
        self._current_state = ThinkingState.SLOW_PROCESSING
        slow_result = self._process_slow_thinking(agent_model, input_object)
        
        self._current_state = ThinkingState.COMPLETED
        return slow_result.to_dict()
