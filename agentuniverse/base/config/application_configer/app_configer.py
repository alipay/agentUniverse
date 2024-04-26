# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 16:17
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: app_configer.py
from typing import Optional
from agentuniverse.base.config.configer import Configer


class AppConfiger(object):
    """The AppConfiger class, which is used to load and manage the application configuration."""

    def __init__(self):
        """Initialize the AppConfiger."""
        self.__configer: Optional[Configer] = None
        self.__base_info_appname: Optional[str] = None
        self.__core_default_package_list: Optional[list[str]] = None
        self.__core_agent_package_list: Optional[list[str]] = None
        self.__core_knowledge_package_list: Optional[list[str]] = None
        self.__core_llm_package_list: Optional[list[str]] = None
        self.__core_planner_package_list: Optional[list[str]] = None
        self.__core_tool_package_list: Optional[list[str]] = None
        self.__core_memory_package_list: Optional[list[str]] = None
        self.__core_service_package_list: Optional[list[str]] = None
        self.__core_prompt_package_list: Optional[list[str]] = None

    @property
    def base_info_appname(self) -> Optional[str]:
        """Return the appname of the application."""
        return self.__base_info_appname

    @property
    def core_default_package_list(self) -> Optional[list[str]]:
        """Return the default package list of the core."""
        return self.__core_default_package_list

    @property
    def core_agent_package_list(self) -> Optional[list[str]]:
        """Return the agent package list of the core."""
        return self.__core_agent_package_list

    @property
    def core_knowledge_package_list(self) -> Optional[list[str]]:
        """Return the knowledge package list of the core."""
        return self.__core_knowledge_package_list

    @property
    def core_llm_package_list(self) -> Optional[list[str]]:
        """Return the llm package list of the core."""
        return self.__core_llm_package_list

    @property
    def core_planner_package_list(self) -> Optional[list[str]]:
        """Return the planner package list of the core."""
        return self.__core_planner_package_list

    @property
    def core_tool_package_list(self) -> Optional[list[str]]:
        """Return the tool package list of the core."""
        return self.__core_tool_package_list

    @property
    def core_memory_package_list(self) -> Optional[list[str]]:
        """Return the memory package list of the core."""
        return self.__core_memory_package_list

    @property
    def core_service_package_list(self) -> Optional[list[str]]:
        """Return the service package list of the core."""
        return self.__core_service_package_list

    @property
    def core_prompt_package_list(self) -> Optional[list[str]]:
        return self.__core_prompt_package_list

    def load_by_configer(self, configer: Configer) -> 'AppConfiger':
        """Load the AppConfiger by the given Configer.

        Args:
            configer(Configer): the Configer object
        Returns:
            AppConfiger: the AppConfiger object
        """
        self.__configer = configer
        self.__base_info_appname = configer.value.get('BASE_INFO', {}).get('appname')
        self.__core_default_package_list = configer.value.get('CORE_PACKAGE', {}).get('default')
        self.__core_agent_package_list = configer.value.get('CORE_PACKAGE', {}).get('agent')
        self.__core_knowledge_package_list = configer.value.get('CORE_PACKAGE', {}).get('knowledge')
        self.__core_llm_package_list = configer.value.get('CORE_PACKAGE', {}).get('llm')
        self.__core_planner_package_list = configer.value.get('CORE_PACKAGE', {}).get('planner')
        self.__core_tool_package_list = configer.value.get('CORE_PACKAGE', {}).get('tool')
        self.__core_memory_package_list = configer.value.get('CORE_PACKAGE', {}).get('memory')
        self.__core_service_package_list = configer.value.get('CORE_PACKAGE', {}).get('service')
        self.__core_prompt_package_list = configer.value.get('CORE_PACKAGE', {}).get('prompt')
        return self
