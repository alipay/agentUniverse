# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 20:47
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_call.py
import asyncio

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager


def batch_call(prompts: list[str], llm_name: str):
    return asyncio.run(async_batch_call(prompts, llm_name))


async def async_batch_call(prompts: list[str], llm_name: str):
    tasks = []

    prompt_len = len(prompts)
    for i in range(0, prompt_len):
        llm: LLM = LLMManager().get_instance_obj(component_instance_name=llm_name, new_instance=True)
        if llm is None:
            raise Exception('LLM not found for agentuniverse data.')
        messages = [{"role": "user", "content": prompts[i]}]
        tasks.append(llm.acall(messages=messages, timeout=700))

    task = asyncio.create_task(show_progress(len(prompts), asyncio.get_running_loop()))
    outputs = await asyncio.gather(*tasks, return_exceptions=True)
    task.cancel()

    results = []
    for i, output in enumerate(outputs):
        if isinstance(output, Exception):
            LOGGER.warn(f'>>>except[async_llm_call]:{output}')
            results.append(None)
        else:
            results.append(output.text)

    print_progress(len(results), prompt_len)

    return results


def print_progress(completed: int, task_count: int):
    progress = (completed / task_count) * 100
    LOGGER.info(f"\r>>>llm progress: {completed}/{task_count} = {progress:.2f}%")


async def show_progress(task_count, loop):
    completed = 0
    while completed < task_count:
        completed_tasks = [t for t in asyncio.all_tasks(loop=loop) if t.done()]
        completed = len(completed_tasks)
        print_progress(completed, task_count)
        await asyncio.sleep(10)
