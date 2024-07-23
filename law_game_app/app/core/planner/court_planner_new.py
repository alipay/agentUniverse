# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/7 10:47
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: court_planner.py
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

default_round = 1


class court_planner_new(Planner):
    """Discussion planner class."""

    # current_round = 0

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
        return self.agents_run(participant_agents, planner_config, agent_model, planner_input)

        # 调用 agents_run 函数并传入事件
        # return self.agents_run_event(participant_agents, planner_config, agent_model, planner_input, event)

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
                   agent_input: dict) -> dict:
        """ Invoke the participant agents and host agent.

        Args:
            participant_agents (dict): Participant agents.
            planner_config (dict): Planner config.
            agent_model (AgentModel): Agent model object.
            agent_input (dict): Agent input object.
        Returns:
            dict: The planner result.
        """
        total_round: int = 1
        chat_history = []
        LOGGER.info(f"The topic of discussion is {agent_input.get(self.input_key)}")
        LOGGER.info(f"The participant agents are {'|'.join(participant_agents.keys())}")
        agent_input['total_round'] = total_round
        agent_input['roles'] = ' and '.join(participant_agents.keys())

        LOGGER.info(f"agent_input \n{agent_input}")

        # event_dispatcher = agent_input["event"]
        for i in range(total_round):
            LOGGER.info("------------------------------------------------------------------")
            LOGGER.info(f"Start a discussion, round is {i + 1}.")

            # event_dispatcher.trigger_event("NEED_INPUT", {"msg":"需要用户输入"})

            # def get_user_input():
            #     agent_input['input'] = q = event_dispatcher.event_queue.get()
            #
            # event_dispatcher.register_listener("USER_INPUT",get_user_input)

            # agent_input['input'] = input()

            for agent_name, agent in participant_agents.items():
                # invoke participant agent
                agent_input['agent_name'] = agent_name
                agent_input['cur_round'] = i + 1
                agent_input['role'] = agent_name
                output_object: OutputObject = agent.run(**agent_input)
                LOGGER.debug(f"output_object {output_object.to_dict()}")


                current_output = output_object.get_data('output', '')

                # process chat history
                chat_history.append({'role':'human','type': 'human','content': agent_input.get('input')})

                cnt = f"第 {i + 1} 回合 agent {agent_name} 发言: {current_output}"
                ai_msg = {'role':agent_name,'type': 'ai','content': cnt}
                chat_history.append(ai_msg)
                agent_input['chat_history'] = chat_history

                LOGGER.info("------------------------------------------------------------------")
                LOGGER.info(f"开始发言: agent is {agent_name}.")
                LOGGER.info(cnt)
                # yield chat_history[-1]
                LOGGER.info(f" for {agent_name} \n{agent_input}")
                LOGGER.info("------------------------------------------------------------------")

                # event_dispatcher.trigger_event("AGENT_CNT", cnt)
                # event_dispatcher.trigger_event("AGENT_CNT", {"msg": f"测试{i} {agent_name}"})
                yield output_object

        agent_input['chat_history'] = chat_history

        for i in agent_input['chat_history']:
            LOGGER.info(f"re chat_history {i}")
        # yield chat_history
        # finally invoke host agent
        # return self.invoke_host_agent(agent_model, agent_input)

    def invoke_host_agent(self, agent_model: AgentModel, planner_input: dict) -> dict:
        """ Invoke the host agent.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
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
        res = asyncio.run(
            chain_with_history.ainvoke(input=planner_input, config={"configurable": {"session_id": "unused"}}))
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
