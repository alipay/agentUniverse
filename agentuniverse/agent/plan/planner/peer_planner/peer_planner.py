# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 10:56
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: peer_planner.py
"""Peer planner module."""
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER

default_sub_agents = {
    'planning': 'PlanningAgent',
    'executing': 'ExecutingAgent',
    'expressing': 'ExpressingAgent',
    'reviewing': 'ReviewingAgent',
}

default_jump_step = 'expressing'

default_eval_threshold = 60

default_retry_count = 2


class PeerPlanner(Planner):
    """Peer planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        Returns:
            dict: The planner result.
        """
        planner_config = agent_model.plan.get('planner')
        sub_agents = self.generate_sub_agents(planner_config)
        return self.agents_run(sub_agents, planner_config, planner_input, input_object)

    @staticmethod
    def generate_sub_agents(planner_config: dict) -> dict:
        """Generate sub agents.

        Args:
            planner_config (dict): Planner config object.
        Returns:
            dict: Planner agents.
        """
        agents = dict()
        for config_key, default_agent in default_sub_agents.items():
            config_data = planner_config.get(config_key, None)
            agents[config_key] = AgentManager().get_instance_obj(config_data if config_data else default_agent)
        return agents

    @staticmethod
    def build_expert_framework(planner_config: dict, input_object: InputObject):
        """Build expert framework for the given planner config object.

        Args:
            planner_config (dict): Planner config object.
            input_object (InputObject): Agent input object.
        """
        expert_framework = planner_config.get('expert_framework')
        if expert_framework:
            context = expert_framework.get('context')
            selector = expert_framework.get('selector')
            if selector:
                selector_result = ToolManager().get_instance_obj(selector).run(**input_object.to_dict())
                input_object.add_data('expert_framework', selector_result)
            elif context:
                input_object.add_data('expert_framework', context)

    def agents_run(self, agents: dict, planner_config: dict, agent_input: dict, input_object: InputObject) -> dict:
        """Planner agents run.

        Args:
            agents (dict): Planner agents.
            planner_config (dict): Planner config object.
            agent_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        Returns:
            dict: The planner result.
        """
        result: dict = dict()

        loopResults = list()
        planning_result = dict()
        executing_result = dict()
        expressing_result = dict()
        reviewing_result = dict()

        retry_count = planner_config.get('retry_count', default_retry_count)
        jump_step = planner_config.get('jump_step', default_jump_step)
        eval_threshold = planner_config.get('eval_threshold', default_eval_threshold)

        self.build_expert_framework(planner_config, input_object)

        planningAgent = agents.get('planning')
        executingAgent = agents.get('executing')
        expressingAgent = agents.get('expressing')
        reviewingAgent = agents.get('reviewing')

        for _ in range(retry_count):
            LOGGER.info(f"Start execution sub agents, retry_count is {_}.")
            if not planning_result or jump_step == "planning":
                if not planningAgent:
                    LOGGER.warn("no planning agent, use default.")
                    planning_result = OutputObject({"framework": [agent_input.get('input')]})
                else:
                    planning_result = planningAgent.run(**input_object.to_dict())

                LOGGER.info(f"Planning agent execution result is {planning_result.to_json_str()}.")
                input_object.add_data('planning_result', planning_result)

            if not executing_result or jump_step in ["planning", "executing"]:
                if not executingAgent:
                    LOGGER.warn("no executing agent, use default.")
                    executing_result = OutputObject({})
                else:
                    executing_result = executingAgent.run(**input_object.to_dict())

                LOGGER.info(f"Executing agent execution result is {executing_result.to_json_str()}.")
                input_object.add_data('executing_result', executing_result)

            if not expressing_result or jump_step in ["planning", "executing", "expressing"]:
                if not expressingAgent:
                    LOGGER.warn("no expression agent, use default.")
                    expressing_result = OutputObject({})
                else:
                    expressing_result = expressingAgent.run(**input_object.to_dict())

                LOGGER.info(f"Expressing agent execution result is {expressing_result.to_json_str()}.")
                input_object.add_data('expressing_result', expressing_result)

            if not reviewing_result or jump_step in ["planning", "executing", "expressing", "reviewing"]:
                if not reviewingAgent:
                    LOGGER.warn("no expression agent, use default.")
                    loopResults.append({
                        "planning_result": planning_result,
                        "executing_result": executing_result,
                        "expressing_result": expressing_result,
                        "reviewing_result": reviewing_result
                    })
                    result['result'] = loopResults
                    return result
                else:
                    reviewing_result = reviewingAgent.run(**input_object.to_dict())

                    LOGGER.info(f"Reviewing agent execution result is {reviewing_result.to_json_str()}.")
                    input_object.add_data('evaluator_result', reviewing_result)
                    if reviewing_result.get_data('score') and reviewing_result.get_data('score') >= eval_threshold:
                        loopResults.append({
                            "planning_result": planning_result,
                            "executing_result": executing_result,
                            "expressing_result": expressing_result,
                            "reviewing_result": reviewing_result
                        })
                        result['result'] = loopResults
                        return result
                    else:
                        loopResults.append({
                            "planning_result": planning_result,
                            "executing_result": executing_result,
                            "expressing_result": expressing_result,
                            "reviewing_result": reviewing_result
                        })
        result['result'] = loopResults
        return result
