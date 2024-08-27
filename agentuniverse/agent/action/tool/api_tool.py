# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from abc import abstractmethod
import json
from typing import Any
from urllib.parse import urlencode

import httpx
from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger

class APITool(Tool):
    """The api tool.
    """      
    def execute(self, tool_input: ToolInput):
        print('执行 API Tool')

