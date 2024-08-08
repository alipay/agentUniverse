# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/13 11:03
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: stream_callback.py

import asyncio
from typing import Optional, Dict, Any, Union
from uuid import UUID

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import GenerationChunk, ChatGenerationChunk


class StreamOutPutCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, queue_stream: asyncio.Queue, color: Optional[str] = None, agent_info: dict = None) -> None:
        """Initialize callback handler."""
        self.queueStream = queue_stream
        self.color = color
        if agent_info is None:
            agent_info = {}
        self.agent_info = agent_info

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        return

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""

    def on_agent_action(
            self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        self.queueStream.put_nowait({
            "type": "ReAct",
            "data": {
                "output": "\nThought:" + action.log,
                "agent_info": self.agent_info
            }
        })

    def on_llm_new_token(
            self,
            token: str,
            *,
            chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        # add token chunk to the queue.
        self.queueStream.put_nowait({
            "type": "token",
            "data": {
                "chunk": chunk.text,
                "agent_info": self.agent_info
            }
        })

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
            self.queueStream.put_nowait({
                "type": "ReAct",
                "data": {
                    "output": '\n' + observation_prefix + output,
                    "agent_info": self.agent_info
                }
            })
        else:
            self.queueStream.put_nowait({
                "type": "ReAct",
                "data": {
                    "output": '\n Observation:' + output,
                    "agent_info": self.agent_info
                }
            })

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
        self.queueStream.put_nowait({
            "type": "ReAct",
            "data": {
                "output": '\nThought:' + finish.output,
                "agent_info": self.agent_info
            }
        })
