#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/17 17:08
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：event_dispatcher.py
from threading import Lock
from typing import Callable, List, Dict

from agentuniverse.base.util.logging.logging_util import LOGGER
from threading import Lock
from queue import Queue

# class EventDispatcher:
#     def __init__(self):
#         self.listeners = []
#
#     def register_listener(self, listener):
#         LOGGER.info("触发 register_listener")
#         self.listeners.append(listener)
#
#     def trigger_event(self, event_data):
#         LOGGER.info("触发 trigger_event")
#
#         for listener in self.listeners:
#             listener(event_data)
from threading import Lock
from collections import defaultdict
from queue import Queue


class EventDispatcher:
    def __init__(self):
        self.listeners: dict = defaultdict(list)
        self.lock = Lock()
        self.event_queue = Queue()
        self.event_store = defaultdict(list)


    def register_listener(self, event_type: str, listener: callable) -> None:
        with self.lock:
            self.listeners[event_type].append(listener)
            LOGGER.info(f"为事件类型 '{event_type}' 注册监听器. 当前监听器数量: {len(self.listeners[event_type])}")

    def trigger_event(self, event_type: str, event_data: dict) -> None:
        with self.lock:
            listeners_copy = self.listeners.get(event_type, [])
            self.event_store[event_type].append(event_data)
            self.event_queue.put((event_type, event_data))

        for listener in listeners_copy:
            try:
                listener(event_data)
                LOGGER.info(f"监听器成功处理事件类型 '{event_type}'")
            except Exception as e:
                LOGGER.error(f"监听器处理事件类型 '{event_type}' 时发生错误: {e}")

    def get_events_by_type(self, event_type: str) -> list:
        """根据事件类型获取所有事件数据"""
        return self.event_store[event_type]

# 创建 EventDispatcher 实例
event_dispatcher = EventDispatcher()