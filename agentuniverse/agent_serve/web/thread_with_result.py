# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/26 14:31
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: thread_with_result.py

from threading import Thread


class ThreadWithReturnValue(Thread):
    """A thread can save the target func exec result."""
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None):
        super().__init__(group, target, name, args, kwargs)

        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs
        self.args = args
        self.target = target
        self._return = None
        self.error = None

    def run(self):
        """Run the target func and save result in _return."""
        if self.target is not None:
            try:
                self._return = self.target(*self.args, **self.kwargs)
            except Exception as e:
                self.error = e

    def result(self):
        """Wait for target func finished, then return the result or raise an
        error."""
        self.join()
        if self.error is not None:
            raise self.error
        return self._return
