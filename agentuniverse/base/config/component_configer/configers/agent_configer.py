# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/13 12:01
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: agent_configer.py
from typing import Optional
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


class AgentConfiger(ComponentConfiger):
    """The AgentConfiger class, which is used to load and manage the Agent configuration."""

    def __init__(self, configer: Optional[Configer] = None):
        """Initialize the AgentConfiger."""
        super().__init__(configer)
        self.__info: Optional[dict] = dict()
        self.__profile: Optional[dict] = dict()
        self.__plan: Optional[dict] = dict()
        self.__memory: Optional[dict] = dict()
        self.__action: Optional[dict] = dict()
        self.__security: Optional[str] = None

    @property
    def memory(self) -> Optional[dict]:
        """Return the name of the Agent."""
        return self.__memory

    @property
    def action(self) -> Optional[dict]:
        """Return the name of the Agent."""
        return self.__action

    @property
    def profile(self) -> Optional[dict]:
        """Return the name of the Agent."""
        return self.__profile

    @property
    def plan(self) -> Optional[dict]:
        """Return the description of the Agent."""
        return self.__plan

    @property
    def info(self) -> Optional[dict]:
        """Return the name of the Agent."""
        return self.__info

    @property
    def security(self) -> Optional[str]:
        """Return the security component of the Agent."""
        return self.__security

    def load(self) -> 'AgentConfiger':
        """Load the configuration by the Configer object.
        Returns:
            AgentConfiger: the AgentConfiger object
        """
        return self.load_by_configer(self.configer)

    def load_by_configer(self, configer: Configer) -> 'AgentConfiger':
        """Load the configuration by the Configer object.
        Args:
            configer(Configer): the Configer object
        Returns:
            AgentConfiger: the AgentConfiger object
        """
        super().load_by_configer(configer)

        try:
            configer_value: dict = configer.value
            self.__info = configer_value.get('info') or self.__info
            self.__profile = configer_value.get('profile') or self.__profile
            self.__plan = configer_value.get('plan') or self.__plan
            self.__memory = configer_value.get('memory') or self.__memory
            self.__action = configer_value.get('action') or self.__action
            self.__security = configer_value.get('security') or self.__security
        except Exception as e:
            raise Exception(f"Failed to parse the Agent configuration: {e}")
        return self
