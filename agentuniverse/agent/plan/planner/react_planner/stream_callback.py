# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/13 11:03
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: stream_callback.py

import asyncio
from typing import Optional, Dict, Any

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler


class StreamOutPutCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, queue_stream: asyncio.Queue, color: Optional[str] = None) -> None:
        """Initialize callback handler."""
        self.queueStream = queue_stream
        self.color = color

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        return

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""

    def on_agent_action(
            self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        self.queueStream.put_nowait("Thought:"+action.log)

    def on_tool_end(
            self,
            output: str,
            color: Optional[str] = None,
            observation_prefix: Optional[str] = None,
            llm_prefix: Optional[str] = None,
            **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        if observation_prefix is not None:
            self.queueStream.put_nowait(observation_prefix + output)
        else:
            self.queueStream.put_nowait('Observation:'+output)

    def on_text(
            self,
            text: str,
            color: Optional[str] = None,
            end: str = "",
            **kwargs: Any,
    ) -> None:
        """Run when agent ends."""

    def on_agent_finish(
            self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        self.queueStream.put_nowait("Thought:" + finish.log + "\n")
