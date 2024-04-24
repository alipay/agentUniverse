# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/9 16:57
# @Author  : jerry.zzw 
# @Email   : jerry.zzw@antgroup.com
# @FileName: server_application.py
import unittest

from sample_standard_app.app.bootstrap.server_application import ServerApplication


def test_app_start():
    ServerApplication.start()
