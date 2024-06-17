# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/17 17:17
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: dedupe.py
from collections import Counter

from simhash import Simhash
from agentuniverse_data.node.data.base.prompt_base import PromptBase


class DedupeNode(PromptBase):
    """The DedupeNode class, which is used to define the class of dedupe node."""

    diversify_hamming_threshold: int = 18
    freq_top_percent: float = 1.0
    freq_least_count: int = 100

    def _node_preprocess(self) -> None:
        super()._node_preprocess()

        self.diversify_hamming_threshold = self._get_node_param('diversify_hamming_threshold')
        self.freq_top_percent = self._get_node_param('freq_top_percent')
        self.freq_least_count = self._get_node_param('freq_least_count')

    def _node_process(self) -> None:
        if not self._prompt_list or len(self._prompt_list) == 0:
            return

        # calculate the simhash value for each document.
        simhashes = [(doc, Simhash(doc)) for doc in self._prompt_list]

        unique_documents = []
        replaced_documents = []
        for doc1, sh1 in simhashes:
            if all(sh1.distance(sh2) > self.diversify_hamming_threshold for _, sh2 in unique_documents):
                unique_documents.append((doc1, sh1))
                dis = sh1.distance(unique_documents[0][1])
            least_hamming = self.diversify_hamming_threshold
            least_hamming_doc = None
            for i in range(0, len(unique_documents)):
                sh2 = unique_documents[i][1]
                hamming_dist = sh1.distance(sh2)
                if hamming_dist < least_hamming:
                    least_hamming = hamming_dist
                    least_hamming_doc = unique_documents[i][0]
            replaced_documents.append(least_hamming_doc)

        freq_counter = Counter(replaced_documents)
        sorted_docs = sorted(freq_counter.items(), key=lambda x: x[1], reverse=True)

        orig_len = len(sorted_docs)
        freq_top_num = int(orig_len * self.freq_top_percent)
        if freq_top_num < self.freq_least_count:
            freq_top_num = self.freq_least_count
        if self.freq_least_count > orig_len:
            freq_top_num = orig_len

        freq_top_docs = sorted_docs[:freq_top_num]

        self._prompt_list = []
        for doc, freq in freq_top_docs:
            if doc is not None:
                self._prompt_list.append(doc)
