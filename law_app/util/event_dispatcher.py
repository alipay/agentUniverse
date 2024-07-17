#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/17 17:08
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：event_dispatcher.py
from agentuniverse.base.util.logging.logging_util import LOGGER


class EventDispatcher:
    def __init__(self):
        self.listeners = []

    def register_listener(self, listener):
        LOGGER.info("触发 register_listener")
        self.listeners.append(listener)

    def trigger_event(self, event_data):
        LOGGER.info("触发 trigger_event")

        for listener in self.listeners:
            listener(event_data)