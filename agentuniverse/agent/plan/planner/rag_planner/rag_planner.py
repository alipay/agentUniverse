# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/25 14:58
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: rag_planner.py
"""Rag planner module."""
import asyncio

from langchain.chains import LLMChain
from langchain_core.memory import BaseMemory

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel


class RagPlanner(Planner):
    """Rag planner class."""

    def invoke(self, agent_model: AgentModel, planner_input: dict,
               input_object: InputObject) -> dict:
        """Invoke the planner.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
            input_object (InputObject): Agent input object.
        Returns:
            dict: The planner result.
        """
        memory: BaseMemory = self.handle_memory(agent_model, planner_input)

        self.handle_all_actions(agent_model, planner_input, input_object)

        llm: LLM = self.handle_llm(agent_model)

        prompt: ChatPrompt = self.handle_prompt(agent_model, planner_input)
        process_llm_token(llm, prompt.as_langchain(), agent_model.profile, planner_input)

        llm_chain = LLMChain(llm=llm.as_langchain(),
                             prompt=prompt.as_langchain(),
                             output_key=self.output_key, memory=memory)

        return asyncio.run(llm_chain.acall(inputs=planner_input))

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
        image_url = planner_input.pop('image_url', '') or ''
        if image_url:
            content = [{"type": "image_url", "image_url": {"url": image_url}}]
            chat_prompt.messages.append(Message(type=ChatMessageEnum.HUMAN.value, content=content))
        return chat_prompt
