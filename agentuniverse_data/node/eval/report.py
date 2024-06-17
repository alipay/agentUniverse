# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 18:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: report.py
from typing import List

from agentuniverse_data.node.base.eval_node_base import EvalNodeBase
from agentuniverse_data.util.fileio.node_msg_jsonl import JsonFileReader


class ReportNode(EvalNodeBase):
    """The ReportNode class, which is used to define the class of report node."""

    _eval_report_json_list: List[str] = None

    def _node_preprocess(self) -> None:
        if not self.datasets_in_jsonl or len(self.datasets_in_jsonl) == 0:
            raise Exception(f"No input datasets: {self.datasets_in_jsonl}")

    def _node_postprocess(self) -> None:
        super()._node_postprocess()

        if self._dataset_out_handler and self._eval_report_json_list:
            self._dataset_out_handler.write_json_obj_list(self._eval_report_json_list)

    def _node_process(self) -> None:
        self._eval_report_json_list = []
        for i in range(0, len(self.datasets_in_jsonl)):
            jfr = JsonFileReader(self.datasets_in_jsonl[i])
            line_objs = jfr.read_json_obj_list()
            if line_objs is None:
                break

            line_num = 0
            total_avg_score = 0.0
            dim_avg_score = {}
            for j in range(0, len(line_objs)):
                json_obj = line_objs[j]
                line_num += 1
                total_avg_score += json_obj['avg_score']
                dimensions = json_obj['dimensions']

                dim_num = len(dimensions)
                for k in range(0, dim_num):
                    name = dimensions[k]['name']
                    score = dimensions[k]['score']
                    if name in dim_avg_score:
                        dim_avg_score[name] += float(score)
                    else:
                        dim_avg_score[name] = float(score)

            for key in dim_avg_score:
                dim_total_score = dim_avg_score[key]
                dim_avg_score[key] = dim_total_score / line_num

            total_avg_score = total_avg_score / line_num

            report_line_obj = {
                'input_file': self.datasets_in_jsonl[i],
                'total_avg_score': total_avg_score,
                'dim_avg_score': dim_avg_score
            }
            self._eval_report_json_list.append(report_line_obj)
