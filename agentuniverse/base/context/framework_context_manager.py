# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/11 16:02
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: framework_context_manager.py

from contextvars import ContextVar, Token
import threading
from typing import Dict, Any

from agentuniverse.base.annotation.singleton import singleton


@singleton
class FrameworkContextManager:
    """A manager class to set, get and clear thread level context."""

    def __init__(self):
        """Init an empty context variable dict and a thread lock used when
        add new key to this dict."""
        self.__context_dict: Dict[str, ContextVar] = {}
        self.__dict_edit_lock = threading.Lock()

    def is_context_exist(self, var_name: str) -> bool:
        """Judge whether context variable exist in current context.

        Args:
            var_name (`str`):
                Name of the context variable.

        Returns:
            A boolean value indicating whether the variable exists.
        """
        return var_name in self.__context_dict

    def set_context(self, var_name: str, var_value: Any) -> Token:
        """Set a context variable value.

        Args:
            var_name (`str`):
                Name of the context variable.
            var_value (`Any`):
                Value of the context variable.
        """
        if var_name not in self.__context_dict:
            with self.__dict_edit_lock:
                if var_name not in self.__context_dict:
                    self.__context_dict[var_name] = ContextVar(var_name)
        return self.__context_dict[var_name].set(var_value)

    def get_context(self,
                    var_name: str,
                    default_value: Any = None):
        """Get a context variable value.

        Args:
            var_name (`str`):
                Name of the context variable.
            default_value (`Any`, defaults to `None`):
                Value to be returned if target context variable doesn't exist.
        """
        if var_name not in self.__context_dict:
            return default_value
        return self.__context_dict[var_name].get(default_value)

    def del_context(self, var_name: str):
        """Set a context variable to None.

        Args:
            var_name (`str`): Name of the context variable.
        """
        if self.is_context_exist(var_name):
            self.__context_dict[var_name].set(None)

    def reset_context(self, var_name: str, token: Token):
        """Reset a context variable using given token.

        Args:
            var_name (`str`):
                Name of the context variable.
            token (`Token`):
                Token used to reset a context variable.
        """
        self.__context_dict[var_name].reset(token)
