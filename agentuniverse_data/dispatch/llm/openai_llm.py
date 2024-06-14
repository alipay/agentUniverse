# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:19
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_llm.py
import asyncio

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.openai_llm import OpenAILLM


class DemoOpenAILLM(OpenAILLM):

    def batch_call(self, prompts: list[str]):
        return asyncio.run(self.async_batch_call(prompts))

    async def async_batch_call(self, prompts: list[str]):
        tasks = []
        prompt_len = len(prompts)
        for i in range(0, prompt_len):
            messages = [{"role": "user", "content": prompts[i]}]
            tasks.append(self.acall(messages=messages, timeout=200))

        task = asyncio.create_task(self.show_progress(len(prompts), asyncio.get_running_loop()))
        outputs = await asyncio.gather(*tasks, return_exceptions=True)
        task.cancel()

        results = []
        for i, output in enumerate(outputs):
            if isinstance(output, Exception):
                LOGGER.warn(f'>>>except[async_llm_call]:{output}')
                results.append(None)
            else:
                results.append(output.text)

        self.print_progress(len(results), prompt_len)

        return results

    def print_progress(self, completed: int, task_count: int):
        progress = (completed / task_count) * 100
        LOGGER.info(f"\r>>>llm progress: {completed}/{task_count} = {progress:.2f}%")

    async def show_progress(self, task_count, loop):
        completed = 0
        while completed < task_count:
            completed_tasks = [t for t in asyncio.all_tasks(loop=loop) if t.done()]
            completed = len(completed_tasks)
            self.print_progress(completed, task_count)
            await asyncio.sleep(10)
