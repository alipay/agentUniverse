# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 10:18
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: web_booster.py

import sys


def start_web_server(**kwargs):
    """Start func of flask server(on windows platform) or gunicorn server(on
    others). Accept input arguments to overwrite default gunicorn config."""
    if sys.platform.startswith('win'):
        from .flask_server import app
        if 'bind' in kwargs:
            host, port = kwargs['bind'].split(':')
            port = int(port)
        else:
            port = 8888
            host = '0.0.0.0'
        app.run(port=port, host=host, debug=False)
    else:
        from .gunicorn_server import GunicornApplication
        GunicornApplication().update_config(kwargs)
        GunicornApplication().run()