#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/16 16:58
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：test.py

class ChatMessage:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content

    def __repr__(self):
        return f"{self.sender}: {self.content}"


def invoke():
    print("inv")
    return agents_run()


def agents_run():
    total_round: int = 3
    chat_history = []

    # 假定有多个代理（agent）和一个主机代理（host agent）
    agents = ["代理1", "代理2", "主机代理"]

    for round_num in range(total_round):
        for agent in agents[:-1]:  # 不包括最后一个主机代理
            message_content = f"第{round_num + 1}轮 - 消息来自{agent}"
            message = ChatMessage(agent, message_content)
            chat_history.append(message)
            yield message

    # 最终由主机代理发出的消息
    final_message_content = "最后一轮 - 消息来自主机代理"
    final_message = ChatMessage(agents[-1], final_message_content)
    chat_history.append(final_message)
    yield final_message

# 调用 invoke() 函数并将生成器的结果迭代出来
x = invoke()
# 迭代生成器的产出
for message in x:
    print(message)