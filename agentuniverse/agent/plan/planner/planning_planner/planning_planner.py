# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/14 16:02
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: planning_planner.py
"""Planning planner module."""
import asyncio
from langchain.chains import LLMChain
from langchain_core.memory import BaseMemory

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.plan.planner.planning_planner.prompt import instruction, target, introduction
from agentuniverse.agent.plan.planner.planner import Planner
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.llm.llm import LLM
from agentuniverse.prompt.prompt_model import AgentPromptModel


class PlanningPlanner(Planner):
    """Planning planner class."""

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

        llm: LLM = self.handle_llm(agent_model)

        self.handle_prompt(agent_model, planner_input)

        llm_chain = LLMChain(llm=llm.as_langchain(),
                             prompt=self.prompt.as_langchain(),
                             output_key=self.output_key, memory=memory)

        return asyncio.run(llm_chain.acall(planner_input))

    def handle_prompt(self, agent_model: AgentModel, planner_input: dict):
        """Prompt module processing.

        Args:
            agent_model (AgentModel): Agent model object.
            planner_input (dict): Planner input object.
        Returns:
            PromptTemplate: The prompt template.
        """
        expert_framework = planner_input.pop('expert_framework', '') or ''

        profile: dict = agent_model.profile

        origin_instruction = profile.get('instruction')
        user_instruction = expert_framework + origin_instruction if origin_instruction else origin_instruction

        user_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                               target=profile.get('target'),
                                                               instruction=user_instruction)

        system_prompt_model: AgentPromptModel = AgentPromptModel(introduction=introduction, target=target,
                                                                 instruction=expert_framework + instruction)
        self.prompt.build_prompt_template(user_prompt_model, system_prompt_model,
                                          self.prompt_assemble_order)
        process_llm_token(self.prompt.as_langchain(), profile, planner_input)
