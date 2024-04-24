# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 14:30
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: reader.py
from abc import abstractmethod
from typing import List, Any

from pydantic import BaseModel

from agentuniverse.agent.action.knowledge.store.document import Document


class Reader(BaseModel):
    """The basic class for the knowledge reader."""

    @abstractmethod
    def load_data(self, *args: Any, **kwargs: Any) -> List[Document]:
        """Load data from the input params."""
