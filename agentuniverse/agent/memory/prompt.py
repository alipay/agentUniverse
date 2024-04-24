# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/14 18:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt.py
from langchain_core.prompts import PromptTemplate

_DEFAULT_EN_SUMMARIZER_TEMPLATE = """Progressively summarize the lines of conversation provided,
 adding onto the previous summary returning a new summary.

EXAMPLE
Current summary:
The human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good.

New lines of conversation:
Human: Why do you think artificial intelligence is a force for good?
AI: Because artificial intelligence will help humans reach their full potential.

New summary:
The human asks what the AI thinks of artificial intelligence.
The AI thinks artificial intelligence is a force for good because it will help humans reach their full potential.
END OF EXAMPLE

Current summary:
{summary}

New lines of conversation:
{new_lines}

New summary:"""

_DEFAULT_CN_SUMMARIZER_TEMPLATE = """逐步总结所提供对话内容，基于先前的概要信息，返回新的概要。

例如：
当前概要:
人类询问AI对人工智能的看法。AI认为人工智能是一股积极的力量。

新一轮对话：
人类：你为什么认为人工智能是一股积极的力量？
AI：因为人工智能将帮助人类发挥他们的全部潜能。

新的概要:
人类询问AI对人工智能的看法。
AI认为人工智能是一股积极的力量，因为它将帮助人们发挥他们的全部潜能。

示例结束。

当前概要:
{summary}

新一轮对话:
{new_lines}

新的概要:"""

SUMMARY_PROMPT = PromptTemplate(
    input_variables=["summary", "new_lines"], template=_DEFAULT_EN_SUMMARIZER_TEMPLATE
)
