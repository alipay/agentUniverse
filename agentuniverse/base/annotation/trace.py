# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/5 15:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: trace.py
import asyncio
import functools
import inspect

from functools import wraps

from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput

monitor = Monitor()


def trace_llm(func):
    """Annotation: @trace_llm

    Decorator to trace the LLM invocation, add llm input and output to the monitor.
    """

    @wraps(func)
    async def wrapper_async(*args, **kwargs):
        # get llm input from arguments
        llm_input = _get_llm_input(func, *args, **kwargs)
        # check whether the tracing switch is enabled
        self = llm_input.pop('self', None)
        if self and hasattr(self, 'tracing'):
            if self.tracing is False:
                return await func(*args, **kwargs)
        # invoke function
        result = await func(*args, **kwargs)
        # not streaming
        if isinstance(result, LLMOutput):
            # add llm invocation info to monitor
            monitor.trace_llm_invocation(source=func.__qualname__, llm_input=llm_input, llm_output=result.text)
            return result
        else:
            # streaming
            async def gen_iterator():
                llm_output = []
                async for chunk in result:
                    llm_output.append(chunk.text)
                    yield chunk
                # add llm invocation info to monitor
                monitor.trace_llm_invocation(source=func.__qualname__, llm_input=llm_input,
                                             llm_output="".join(llm_output))

            return gen_iterator()

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # get llm input from arguments
        llm_input = _get_llm_input(func, *args, **kwargs)
        # check whether the tracing switch is enabled
        self = llm_input.pop('self', None)
        if self and hasattr(self, 'tracing'):
            if not self.tracing:
                return func(*args, **kwargs)
        # invoke function
        result = func(*args, **kwargs)
        # not streaming
        if isinstance(result, LLMOutput):
            # add llm invocation info to monitor
            monitor.trace_llm_invocation(source=func.__qualname__, llm_input=llm_input, llm_output=result.text)
            return result
        else:
            # streaming
            def gen_iterator():
                llm_output = []
                for chunk in result:
                    llm_output.append(chunk.text)
                    yield chunk
                # add llm invocation info to monitor
                monitor.trace_llm_invocation(source=func.__qualname__, llm_input=llm_input,
                                             llm_output="".join(llm_output))

            return gen_iterator()

    if asyncio.iscoroutinefunction(func):
        # async function
        return wrapper_async
    else:
        # sync function
        return wrapper_sync


def _get_llm_input(func, *args, **kwargs) -> dict:
    """Get the llm input from arguments."""
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    return {k: v for k, v in bound_args.arguments.items()}
