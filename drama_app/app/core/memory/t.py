#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/8/2 10:32
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：t.py
import getpass
import os

# 设置 OpenAI API 密钥
os.environ["OPENAI_API_KEY"] = getpass.getpass(prompt="Please enter your OpenAI API key: ")

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

# 删除现有的 SQLite 文件（如果存在）
import os
if os.path.exists('memory.db'):
    os.remove('memory.db')

# 创建一个函数来获取会话历史记录
def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, "sqlite:///memory.db")

# 初始化 ChatOpenAI 模型
llm = ChatOpenAI(model="gpt-4o-mini")

# 包装 ChatOpenAI 模型，使其能够处理消息历史记录
runnable_with_history = RunnableWithMessageHistory(
    llm,
    get_session_history,
)

# 第一个会话
response = runnable_with_history.invoke(
    [HumanMessage(content="Hi - I'm Bob!")],
    config={"configurable": {"session_id": "1"}},
)
print("Response:", response.content)

response = runnable_with_history.invoke(
    [HumanMessage(content="What's my name?")],
    config={"configurable": {"session_id": "1"}},
)
print("Response:", response.content)

# 第二个会话
response = runnable_with_history.invoke(
    [HumanMessage(content="What's my name?")],
    config={"configurable": {"session_id": "1a"}},
)
print("Response:", response.content)-mini")