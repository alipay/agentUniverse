# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/22 15:52
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: query.py

from typing import Optional, List

from pydantic import BaseModel, Field


class Query(BaseModel):
    """The basic class for the knowledge query.

    Attributes:
        query_str (Optional[str]): The query string.
        similarity_top_k (int): The number of top results to return.
        embedding (List[float]): The specific embedding data of the query.
    """

    query_str: Optional[str] = None
    similarity_top_k: int = 2
    embedding: List[float] = Field(default_factory=list)
