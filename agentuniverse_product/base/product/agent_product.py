# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/25 22:50
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_product.py
from typing import Optional

from agentuniverse.agent.agent import Agent
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse_product.base.product.product import Product


class AgentProduct(Product):
    """The basic class of the agent product."""

    opening_speech: Optional[str] = None
    _instance: Optional[Agent] = None

    @property
    def instance(self) -> Agent:
        return self._instance

    def get_instance_code(self) -> str:
        """Return the full name of the product."""
        appname = ApplicationConfigManager().app_configer.base_info_appname
        return f"{appname}.product.{self.nickname}"
