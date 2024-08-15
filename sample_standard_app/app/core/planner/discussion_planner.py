# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/7 10:47
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_planner.py
import asyncio

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.chat_memory import ChatMemory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.memory_util import generate_memories
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel

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
        # generate participant agents
        participant_agents = self.generate_participant_agents(planner_config)
        # invoke agents
        return self.agents_run(participant_agents, planner_config, agent_model, planner_input, input_object)

    @staticmethod
    def generate_participant_agents(planner_config: dict) -> dict:
        """Generate participant agents."""
        participant = planner_config.get('participant', {})
        participant_names = participant.get('name', [])
        if len(participant_names) == 0:
            raise NotImplementedError
        agents = dict()
        for participant_name in participant_names:
            agents[participant_name] = AgentManager().get_instance_obj(participant_name)
        return agents

    def agents_run(self, participant_agents: dict, planner_config: dict, agent_model: AgentModel,
                   agent_input: dict, input_object: InputObject) -> dict:
        """ Invoke the participant agents and host agent.

        Args:
            participant_agents (dict): Participant agents.
            planner_config (dict): Planner config.
            agent_model (AgentModel): Agent model object.
            agent_input (dict): Agent input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        total_round: int = planner_config.get('round', default_round)
        chat_history = []
        LOGGER.info(f"The topic of discussion is {agent_input.get(self.input_key)}")
        LOGGER.info(f"The participant agents are {'|'.join(participant_agents.keys())}")

        input_object.add_data('chat_history', chat_history)
        input_object.add_data('total_round', total_round)
        input_object.add_data('participants', ' and '.join(participant_agents.keys()))

        for i in range(total_round):
            LOGGER.info("------------------------------------------------------------------")
            LOGGER.info(f"Start a discussion, round is {i + 1}.")
            for agent_name, agent in participant_agents.items():
                LOGGER.info("------------------------------------------------------------------")
                LOGGER.info(f"Start speaking: agent is {agent_name}.")
                LOGGER.info("------------------------------------------------------------------")
                # invoke participant agent
                input_object.add_data('agent_name', agent_name)
                input_object.add_data('cur_round', i + 1)
                output_object: OutputObject = agent.run(**input_object.to_dict())
                current_output = output_object.get_data('output', '')

                # process chat history
                chat_history.append({'content': agent_input.get('input'), 'type': 'human'})
                chat_history.append(
                    {'content': f'the round {i + 1} agent {agent_name} thought: {current_output}', 'type': 'ai'})
                input_object.add_data('chat_history', chat_history)

                # add to the stream queue.
                self.stream_output(input_object, {"data": {
                    'output': current_output,
                    "agent_info": agent_model.info
                }, "type": "participant_agent"})
                LOGGER.info(f"the round {i + 1} agent {agent_name} thought: {output_object.get_data('output', '')}")

        # concatenate the agent input parameters of the host agent.
        agent_input['chat_history'] = chat_history
        agent_input['total_round'] = total_round
        agent_input['participants'] = ' and '.join(participant_agents.keys())

        # finally invoke host agent
        return self.invoke_host_agent(agent_model, agent_input, input_object)

    def invoke_host_agent(self, agent_model: AgentModel, planner_input: dict, input_object: InputObject) -> dict:
        """ Invoke the host agent.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The planner result.
        """
        LOGGER.info("------------------------------------------------------------------")
        LOGGER.info(f"Discussion end.")
        LOGGER.info(f"Host agent starts summarize the discussion.")
        LOGGER.info("------------------------------------------------------------------")
        memory: ChatMemory = self.handle_memory(agent_model, planner_input)

        llm: LLM = self.handle_llm(agent_model)

        prompt: ChatPrompt = self.handle_prompt(agent_model, planner_input)
        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)

        chat_history = memory.as_langchain().chat_memory if memory else InMemoryChatMessageHistory()

        chain_with_history = RunnableWithMessageHistory(
            prompt.as_langchain() | llm.as_langchain(),
            lambda session_id: chat_history,
            history_messages_key="chat_history",
            input_messages_key=self.input_key,
        ) | StrOutputParser()
        res = self.invoke_chain(agent_model, chain_with_history, planner_input, chat_history, input_object)
        LOGGER.info(f"Discussion summary is: {res}")
        return {**planner_input, self.output_key: res, 'chat_history': generate_memories(chat_history)}

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict) -> ChatPrompt:
        """Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            ChatPrompt: The chat prompt instance.
        """
        profile: dict = agent_model.profile

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile.get('instruction'))

        # get the prompt by the prompt version
        prompt_version: str = profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, self.prompt_assemble_order)
        image_urls: list = planner_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)
        return chat_prompt
