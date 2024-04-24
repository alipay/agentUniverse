# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/13 15:22
# @Author  : heji
# @Email   : lc299034@antgroup.com
# @FileName: prompt_base.py
"""Prompt base module."""
import re
from typing import Optional

from langchain_core.prompts import PromptTemplate

from agentuniverse.base.component.component_base import ComponentBase
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.util.prompt_util import generate_template
from agentuniverse.prompt.prompt_model import AgentPromptModel


class Prompt(ComponentBase):
    """Prompt class."""

    prompt_template: Optional[str] = None
    input_variables: Optional[list[str]] = None
    component_type: ComponentEnum = ComponentEnum.DEFAULT

    def as_langchain(self) -> PromptTemplate:
        """Convert the prompt template into a LangChain prompt template.

        Returns:
            PromptTemplate: The prompt template.
        """
        return PromptTemplate(template=self.prompt_template,
                              input_variables=self.input_variables)

    def build_prompt_template(self, user_agent_prompt_model: AgentPromptModel,
                              system_agent_prompt_model: AgentPromptModel,
                              prompt_assemble_order: list[str]):
        """Build the prompt template.

        Args:
            user_agent_prompt_model (AgentPromptModel): The user agent prompt model.
            system_agent_prompt_model (AgentPromptModel): The system agent prompt model.
            prompt_assemble_order (list[str]): The prompt assemble ordered list.

        Returns:
            PromptTemplate: The prompt template.
        """
        agent_prompt_model = user_agent_prompt_model + system_agent_prompt_model
        self.prompt_template = generate_template(agent_prompt_model, prompt_assemble_order)
        self.input_variables = re.findall(r'\{(.*?)}', self.prompt_template)
