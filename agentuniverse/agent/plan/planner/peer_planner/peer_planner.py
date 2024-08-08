# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 10:56
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: peer_planner.py
"""Peer planner module."""
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.agent import Agent
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
            input_object (InputObject): The input parameters passed by the user.
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
            if config_data == '':
                continue
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

    def agents_run(self, agents: dict, planner_config: dict, agent_input: dict,
                   input_object: InputObject) -> dict:
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

        planningAgent: Agent = agents.get('planning')
        executingAgent: Agent = agents.get('executing')
        expressingAgent: Agent = agents.get('expressing')
        reviewingAgent: Agent = agents.get('reviewing')

        for _ in range(retry_count):
            LOGGER.info(f"Starting peer agents, retry_count is {_ + 1}.")
            if not planning_result or jump_step == "planning":
                if not planningAgent:
                    LOGGER.warn("no planning agent.")
                    planning_result = OutputObject({"framework": [agent_input.get('input')]})
                else:
                    LOGGER.info(f"Starting planning agent.")
                    planning_result = planningAgent.run(**input_object.to_dict())

                input_object.add_data('planning_result', planning_result)
                # add planning agent log info
                logger_info = f"\nPlanning agent execution result is :\n"
                for index, one_framework in enumerate(planning_result.get_data('framework')):
                    logger_info += f"[{index + 1}] {one_framework} \n"
                LOGGER.info(logger_info)

                # add planning agent intermediate steps
                if planningAgent:
                    self.stream_output(input_object, {"data": {
                        'output': planning_result.get_data('framework'),
                        "agent_info": planningAgent.agent_model.info
                    }, "type": "planning"})

            if not executing_result or jump_step in ["planning", "executing"]:
                if not executingAgent:
                    LOGGER.warn("no executing agent.")
                    executing_result = OutputObject({})
                else:
                    LOGGER.info(f"Starting executing agent.")
                    executing_result = executingAgent.run(**input_object.to_dict())

                input_object.add_data('executing_result', executing_result)
                # add executing agent log info
                logger_info = f"\nExecuting agent execution result is :\n"
                if executing_result.get_data('executing_result'):
                    for index, one_exec_res in enumerate(executing_result.get_data('executing_result')):
                        one_exec_log_info = f"[{index + 1}] input: {one_exec_res['input']}\n"
                        one_exec_log_info += f"[{index + 1}] output: {one_exec_res['output']}\n"
                        logger_info += one_exec_log_info
                LOGGER.info(logger_info)

                # add executing agent intermediate steps
                if executingAgent:
                    self.stream_output(input_object, {"data": {
                        'output': executing_result.get_data('executing_result'),
                        "agent_info": executingAgent.agent_model.info
                    }, "type": "executing"})

            if not expressing_result or jump_step in ["planning", "executing", "expressing"]:
                if not expressingAgent:
                    LOGGER.warn("no expressing agent.")
                    expressing_result = OutputObject({})
                else:
                    LOGGER.info(f"Starting expressing agent.")
                    expressing_result = expressingAgent.run(**input_object.to_dict())

                input_object.add_data('expressing_result', expressing_result)
                # add expressing agent log info
                logger_info = f"\nExpressing agent execution result is :\n"
                logger_info += f"{expressing_result.get_data('output')}"
                LOGGER.info(logger_info)

                # add expressing agent intermediate steps
                if expressingAgent:
                    self.stream_output(input_object, {"data": {
                        'output': expressing_result.get_data('output'),
                        "agent_info": expressingAgent.agent_model.info
                    }, "type": "expressing"})

            if not reviewing_result or jump_step in ["planning", "executing", "expressing", "reviewing"]:
                if not reviewingAgent:
                    LOGGER.warn("no reviewing agent.")
                    loopResults.append({
                        "planning_result": planning_result,
                        "executing_result": executing_result,
                        "expressing_result": expressing_result,
                        "reviewing_result": reviewing_result
                    })
                    result['result'] = loopResults
                    return result
                else:
                    LOGGER.info(f"Starting reviewing agent.")
                    reviewing_result = reviewingAgent.run(**input_object.to_dict())

                    input_object.add_data('reviewing_result', reviewing_result)

                    # add reviewing agent log info
                    logger_info = f"\nReviewing agent execution result is :\n"
                    reviewing_info_str = f"review suggestion: {reviewing_result.get_data('suggestion')} \n"
                    reviewing_info_str += f"review score: {reviewing_result.get_data('score')} \n"
                    LOGGER.info(logger_info + reviewing_info_str)

                    # add reviewing agent intermediate steps
                    self.stream_output(input_object,
                                       {"data": {
                                           'output': reviewing_result.get_data('suggestion'),
                                           "agent_info": reviewingAgent.agent_model.info
                                       }, "type": "reviewing"})

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
