# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/1/22 16:30
# @Author  : [Your Name]
# @FileName: dual_system_planner.py

"""Dual System planner module implementing fast/slow thinking."""

from typing import Dict, Any, Optional
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.agent.default.fast_thinking_agent.fast_thinking_agent import FastThinkingAgent
from agentuniverse.base.util.logging.logging_util import LOGGER

from .system_types import SystemType, ThinkingState
from .thinking_result import ThinkingResult


class DualSystemPlanner(Planner):
    """Dual system planner implementing System 1 (fast) and System 2 (slow) thinking."""
    
    def __init__(self):
        super().__init__()
        self._current_state = ThinkingState.EVALUATING
        self._confidence_threshold = 0.7  # Configurable threshold
        
    def stream_output(self, input_object: InputObject, output_data: Dict[str, Any]) -> None:
        """Stream intermediate outputs during processing.
        
        Args:
            input_object: The input object containing stream callback
            output_data: Data to be streamed
        """
        stream_callback = input_object.get_data('stream_callback')
        if stream_callback and callable(stream_callback):
            stream_callback(output_data)
            
    def _process_fast_thinking(self, agent_model: Agent, input_object: InputObject) -> ThinkingResult:
        """Process input using System 1 (fast thinking).
        
        Args:
            agent_model: The agent model to use
            input_object: Input parameters
            
        Returns:
            ThinkingResult containing the fast thinking output
        """
        fast_agent = FastThinkingAgent()
        result = fast_agent.run(**input_object.to_dict())
        
        # Stream the fast thinking output
        self.stream_output(input_object, {
            "data": {
                "output": result.get_data('output'),
                "confidence": result.get_data('confidence', 0.0),
                "agent_info": fast_agent.agent_model.info
            },
            "type": "fast_thinking"
        })
        
        return ThinkingResult(
            system_type=SystemType.FAST,
            output=result.get_data('output'),
            confidence=result.get_data('confidence', 0.0),
            thought=result.get_data('thought')
        )
        
    def _process_slow_thinking(self, agent_model: Agent, input_object: InputObject) -> ThinkingResult:
        """Process input using System 2 (slow thinking).
        
        Args:
            agent_model: The agent model to use
            input_object: Input parameters
            
        Returns:
            ThinkingResult containing the slow thinking output
        """
        result = agent_model.run(**input_object.to_dict())
        
        # Stream the slow thinking output
        self.stream_output(input_object, {
            "data": {
                "output": result.get_data('output'),
                "agent_info": agent_model.info
            },
            "type": "slow_thinking"
        })
        
        return ThinkingResult(
            system_type=SystemType.SLOW,
            output=result.get_data('output'),
            confidence=1.0,  # System 2 is assumed to be more thorough
            thought=result.get_data('thought')
        )

    def invoke(self, agent_model: Agent, planner_input: dict, input_object: InputObject) -> dict:
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
        self._current_state = ThinkingState.FAST_THINKING
        fast_result = self._process_fast_thinking(agent_model, input_object)
        
        # If fast thinking is confident enough, return its result
        if fast_result.confidence >= self._confidence_threshold:
            self._current_state = ThinkingState.COMPLETED
            return fast_result.to_dict()
            
        # Otherwise, use slow thinking (System 2)
        self._current_state = ThinkingState.SLOW_THINKING
        slow_result = self._process_slow_thinking(agent_model, input_object)
        
        self._current_state = ThinkingState.COMPLETED
        return slow_result.to_dict()
