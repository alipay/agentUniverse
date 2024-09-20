# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/6 22:05
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: host_agent.py
from collections import deque
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSerializable

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.base.util.agent_util import handle_memory, assemble_memory_output, stream_output, handle_llm, \
    assemble_memory_input
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel

default_round = 2


class HostAgent(Agent):

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['input']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object(InputObject): input parameters passed by the user.
            agent_input(dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        agent_input['input'] = input_object.get_data('input')
        agent_input['participants'] = input_object.get_data('participants')
        agent_input['total_round'] = input_object.get_data('total_round')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        return planner_result

    def execute(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_profile = self.agent_model.profile
        # generate participant agents
        participant_agents = self.generate_participant_agents(agent_profile)
        # invoke agents
        return self.agents_run(participant_agents, agent_profile, agent_input, input_object)

    @staticmethod
    def generate_participant_agents(agent_profile_config: dict) -> dict:
        """Generate participant agents."""
        participant = agent_profile_config.get('discussion_participant', {})
        participant_names = participant.get('name', [])
        if len(participant_names) == 0:
            raise NotImplementedError
        agents = dict()
        for participant_name in participant_names:
            agents[participant_name] = AgentManager().get_instance_obj(participant_name)
        return agents

    def agents_run(self, participant_agents: dict, agent_profile_config: dict,
                   agent_input: dict, input_object: InputObject) -> dict:
        """ Invoke the participant agents and host agent.

        Args:
            participant_agents (dict): Participant agents.
            agent_profile_config (dict): Agent profile config.
            agent_input (dict): Agent input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The agent result.
        """
        total_round: int = agent_profile_config.get('discussion_round', default_round)
        LOGGER.info(f"The topic of discussion is {agent_input.get('input')}")
        LOGGER.info(f"The participant agents are {'|'.join(participant_agents.keys())}")

        # The memory list is used to store memory information that will be passed between participant agents.
        shared_memory_list = deque(maxlen=len(participant_agents) - 1)

        input_object.add_data('total_round', total_round)
        input_object.add_data('participants', ' and '.join(participant_agents.keys()))

        # get the host agent memory.
        host_agent_memory: Memory = handle_memory(self.agent_model, agent_input)

        for i in range(total_round):
            LOGGER.info("------------------------------------------------------------------")
            LOGGER.info(f"Start a discussion, round is {i + 1}.")
            for participant_agent_name, participant_agent in participant_agents.items():
                LOGGER.info("------------------------------------------------------------------")
                LOGGER.info(f"Start speaking: agent is {participant_agent_name}.")
                LOGGER.info("------------------------------------------------------------------")

                # invoke participant agent
                input_object.add_data('chat_history', shared_memory_list)
                input_object.add_data('agent_name', participant_agent_name)
                input_object.add_data('cur_round', i + 1)
                output_object: OutputObject = participant_agent.run(**input_object.to_dict())

                # get the string output.
                current_output = output_object.get_data('output', '')

                # add the memory to the host agent memory instance.
                memory_content = (
                    f"the round {i + 1} participant agent in discussion group is: {participant_agent_name}, "
                    f"Human: {agent_input.get('input')}, AI: {current_output}")
                # append the current memory to the shared memory list.
                shared_memory_list = assemble_memory_output(host_agent_memory,
                                                            agent_input,
                                                            memory_content,
                                                            participant_agent_name,
                                                            shared_memory_list)

                # add to the stream queue.
                stream_output(input_object, {"data": {
                    'output': current_output,
                    "agent_info": self.agent_model.info
                }, "type": "participant_agent"})

                LOGGER.info(
                    f"the round {i + 1} agent {participant_agent_name} thought: {output_object.get_data('output', '')}")

        # concatenate the agent input parameters of the host agent.
        agent_input['total_round'] = total_round
        agent_input['participants'] = ' and '.join(participant_agents.keys())

        # finally invoke host agent
        return self.host_agent_run(agent_input, input_object)

    def host_agent_run(self, agent_input: dict, input_object: InputObject) -> dict:
        """ Invoke the host agent.

        Args:
            agent_input (dict): Agent input object.
            input_object (InputObject): The input parameters passed by the user.
        Returns:
            dict: The agent result.
        """
        LOGGER.info("------------------------------------------------------------------")
        LOGGER.info(f"Discussion end.")
        LOGGER.info(f"Host agent starts summarize the discussion.")
        LOGGER.info("------------------------------------------------------------------")
        memory: Memory = handle_memory(self.agent_model, agent_input)

        llm: LLM = handle_llm(self.agent_model)

        prompt: ChatPrompt = self.handle_prompt(agent_input)
        process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)

        memory_messages = assemble_memory_input(memory, agent_input)

        chain = prompt.as_langchain() | llm.as_langchain_runnable(self.agent_model.llm_params()) | StrOutputParser()
        res = self.invoke_chain(chain, agent_input, input_object)

        content = (f"human: {agent_input.get('input')}, "
                   f"ai: after several rounds of discussions among the participants, "
                   f"the host in the discussion group came to the conclusion:{res}")

        memory_messages = assemble_memory_output(memory, agent_input, content, '', memory_messages)

        LOGGER.info(f"Discussion summary is: {res}")
        return {**agent_input, 'output': res, 'chat_history': memory_messages}

    def handle_prompt(self, agent_input: dict) -> ChatPrompt:
        """Prompt module processing.

        Args:
            agent_input (dict): Agent input object.
        Returns:
            ChatPrompt: The chat prompt instance.
        """
        profile: dict = self.agent_model.profile

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

        chat_prompt = ChatPrompt().build_prompt(profile_prompt_model, ['introduction', 'target', 'instruction'])
        image_urls: list = agent_input.pop('image_urls', []) or []
        if image_urls:
            chat_prompt.generate_image_prompt(image_urls)
        return chat_prompt

    def invoke_chain(self, chain: RunnableSerializable[Any, str], agent_input: dict, input_object: InputObject):

        if not input_object.get_data('output_stream'):
            res = chain.invoke(input=agent_input)
            return res
        result = []
        for token in chain.stream(input=agent_input):
            stream_output(input_object, {
                'type': 'token',
                'data': {
                    'chunk': token,
                    'agent_info': self.agent_model.info
                }
            })
            result.append(token)
        return "".join(result)
