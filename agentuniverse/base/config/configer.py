# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/12 14:29
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: config_manager.py
import re
from typing import Optional, Callable
import tomli
import yaml

from agentuniverse.base.config.config_type_enum import ConfigTypeEnum


class Configer(object):
    """Configger object, responsible for the configuration file load, update, etc."""

    # List of supported file formats
    __SUPPORTED_FILE_FORMATS = [ConfigTypeEnum.TOML.value, ConfigTypeEnum.YAML.value]

    def __init__(self,
                 path: str = None):
        """Initialize the ConfigManager
        Args:
            path(str): the path of the configuration file
        Returns:
            None
        """
        self.__path: str = path
        self.__value: dict = {}

    @property
    def path(self):
        """Return the path of the configuration file"""
        return self.__path

    @path.setter
    def path(self, path: str):
        """Set the path of the configuration file
        Args:
            path(str): the path of the configuration file
        Returns:
            None
        """
        self.__path = path

    @property
    def value(self):
        """Return the value of the configuration file"""
        return self.__value

    @value.setter
    def value(self, value: dict):
        """Set the value of the configuration file
        Args:
            value(dict): the value of the configuration file
        Returns:
            None
        """
        self.__value = value

    def load_by_path(self, path: str) -> 'Configer':
        """Load the configuration file by the given path
        Args:
            path(str): the path of the configuration file
        Returns:
            Configer: the Configer object
        """
        # Check the file format.
        file_format = path.split('.')[-1]
        if file_format not in self.__SUPPORTED_FILE_FORMATS:
            raise ValueError(f"Unsupported file format: {file_format}")

        # Choose the load method according to the file format.
        load_method = self.__choice_load_method(path)
        config_data = load_method(path)
        self.__value = config_data
        return self

    def load(self) -> 'Configer':
        """Load the configuration file

        Returns:
            Configer: the Configer object
        """
        return self.load_by_path(self.__path)

    def get(self, key: str, default=None) -> Optional[any]:
        """Return the value of the configuration file at the given key, or the default value if the key is not found
        Args:
            key(str): the key of the configuration file
            default(any): the default value
        Returns:
            Optional[any]: the value of the configuration file at the given key
        """
        return self.__value.get(key, default)

    def set(self, key: str, value):
        """Set the value of the configuration file at the given key.

        Args:
            key(str): the key of the configuration file
            value(any): the value of the configuration file
        Returns:
            None
        """
        self.__value[key] = value
        pass

    def to_dict(self) -> dict:
        """Return the dictionary representation of the configuration file.

        Returns:
            dict: the dictionary representation of the configuration file
        """
        return self.__value

    def __choice_load_method(self, path: str) -> Optional[Callable]:
        """Choose the load method according to the file format.

        Args:
            path(str): the path of the configuration file
        Returns:
            Optional[Callable]: the load method
        """
        # Define the regular expression and the corresponding method map.
        toml_re = re.compile(r'.*\.toml')
        yaml_re = re.compile(r'.*\.yaml')

        re_method_map = {
            toml_re: self.__load_toml_file,
            yaml_re: self.__load_yaml_file
        }
        for re_compile, method in re_method_map.items():
            if re_compile.search(path):
                return method

    @staticmethod
    def __load_toml_file(path: str) -> dict:
        """Load the toml file.

        Args:
            path(str): the path of the toml file
        Returns:
            dict: the value of the toml file
        """
        with open(path, 'rb') as f:
            config_data = tomli.load(f)
        return config_data

    @staticmethod
    def __load_yaml_file(path: str) -> dict:
        """Load the yaml file.

        Args:
            path(str): the path of the yaml file
        Returns:
            dict: the value of the yaml file
        """
        with open(path, 'r', encoding='utf-8') as stream:
            config_data = yaml.safe_load(stream)
        return config_data
