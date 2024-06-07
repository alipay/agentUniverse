# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/7 10:47
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_planner.py
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER

default_round = 2


class DiscussionPlanner(Planner):
    """Discussion planner class."""

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
        participant_agents = self.generate_participant_agents(planner_config)
        return self.agents_run(participant_agents, planner_config, planner_input, input_object)

    @staticmethod
    def generate_participant_agents(planner_config: dict) -> dict:
        participant = planner_config.get('participant', {})
        participant_names = participant.get('name', [])
        if len(participant_names) == 0:
            raise NotImplementedError
        agents = dict()
        for participant_name in participant_names:
            agents[participant_name] = AgentManager().get_instance_obj(participant_name)
        return agents

    @staticmethod
    def agents_run(agents: dict, planner_config: dict, agent_input: dict, input_object: InputObject) -> dict:
        result: dict = dict()
        total_round: int = planner_config.get('round', default_round)
        chat_history = []
        for i in range(total_round):
            LOGGER.info(f"Start a discussion, round is {i + 1}.")
            for agent_name, agent in agents.items():
                LOGGER.info(f"Start speaking: agent is {agent_name}.")

                # invoke agent
                agent_input['agent_name'] = agent_name
                agent_input['total_round'] = total_round
                agent_input['cur_round'] = i + 1
                output_object: OutputObject = agent.run(**agent_input)
                current_output = output_object.get_data('output', '')

                chat_history.append({'content': agent_input.get('input'), 'type': 'human'})
                chat_history.append(
                    {'content': f'the {i + 1} round agent {agent_name} thought: {current_output}.', 'type': 'ai'})
                agent_input['chat_history'] = chat_history

                # get the result
                result = output_object.to_dict()
                LOGGER.info(f"agent {agent_name} thought: {output_object.get_data('output', '')}.")
        return result
