# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/19 18:18
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: executing_agent.py
"""Executing Agent module."""
import copy
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from typing import Optional, Any
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planner_manager import PlannerManager


class ExecutingAgent(Agent):
    """Executing Agent class."""

    executor: Optional[Any] = ThreadPoolExecutor(max_workers=10, thread_name_prefix="executing_agent")

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['planning_result']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['executing_result']

    def parse_input(self, input_object: InputObject, planner_input: dict) -> dict:
        """Planner parameter parsing.

        Args:
            input_object(InputObject): agent parameter object
            planner_input(dict): Planner input
        Returns:
            dict: Planner input
        """
        planner_input['input'] = input_object.get_data('input')
        planner_input['framework'] = input_object.get_data('planning_result').get_data('framework')
        self.agent_model.profile.setdefault('prompt_version', 'default_executing_agent.cn')
        return planner_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        llm_result = []
        executing_result = []
        futures = planner_result.get('futures')
        for future in futures:
            task_result = future.result()
            llm_result.append(task_result)
            executing_result.append({
                'input': task_result['input'], 'output': task_result['output']
            })

        return {'executing_result': executing_result, 'llm_result': llm_result}

    def execute(self, input_object: InputObject) -> dict:
        """Execute agent instance.

        Args:
            input_object(InputObject): agent parameter object
        Returns:
            dict: Agent result object.
        """
        planning_result = input_object.get_data('planning_result')
        framework = planning_result.get_data('framework', [])
        futures = []
        for task in framework:
            input_object_copy: InputObject = copy.deepcopy(input_object)
            input_object_copy.add_data('input', task)
            planner_input = super().pre_parse_input(input_object_copy)
            futures.append(
                self.executor.submit(
                    PlannerManager().get_instance_obj(self.agent_model.plan.get('planner').get('name')).invoke,
                    self.agent_model, planner_input, input_object_copy))
        wait(futures, return_when=ALL_COMPLETED)
        return self.parse_result({'futures': futures})
