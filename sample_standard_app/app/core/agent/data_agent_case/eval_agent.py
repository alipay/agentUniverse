# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/7/1 17:00
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: eval_agent.py
from typing import Tuple, List

import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_core.utils.json import parse_json_markdown
from openpyxl.reader.excel import load_workbook

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.input_object import InputObject
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt import Prompt
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from sample_standard_app.app.util.jsonl_file_utils import JsonFileWriter


class EvalAgent(Agent):
    """Evaluation Agent class."""

    def input_keys(self) -> list[str]:
        """Return the input keys of the Agent."""
        return ['prompt_answer_list']

    def output_keys(self) -> list[str]:
        """Return the output keys of the Agent."""
        return ['eval_report_json_list', 'eval_dims_json_list']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        """Agent parameter parsing.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input preparsed by the agent.
        Returns:
            dict: agent input parsed from `input_object` by the user.
        """
        agent_input['prompt_answer_list'] = input_object.get_data('prompt_answer_list')
        return agent_input

    def parse_result(self, planner_result: dict) -> dict:
        """Planner result parser.

        Args:
            planner_result(dict): Planner result
        Returns:
            dict: Agent result object.
        """
        return planner_result

    def execute(self, input_object: InputObject, agent_input: dict):
        """Execute agent instance.

        Args:
            input_object (InputObject): input parameters passed by the user.
            agent_input (dict): agent input parsed from `input_object` by the user.
        """
        LOGGER.info("-------------------------------------------")
        LOGGER.info(f"Start: use the evaluator agent to evaluate q&a dataset.")
        LOGGER.info("-------------------------------------------")

        prompt_answer_list: List[List[Tuple[str, str]]] = input_object.get_data('prompt_answer_list')
        max_eval_lines = self.agent_model.profile.get('max_eval_lines', 100)
        if len(prompt_answer_list) == 0:
            raise ValueError('the `prompt_answer_list` is empty')

        # step1: evaluate the dataset in multiple dimensions and give specific scores.
        eval_dims_json_list: List[List[dict]] = self.eval(prompt_answer_list, max_eval_lines)
        LOGGER.info(f"End: evaluate the dataset in multiple dimensions done.")

        LOGGER.info("-------------------------------------------")
        # step2: write the eval results to excel file.
        self.generate_eval_results_excel(prompt_answer_list, eval_dims_json_list)

        # step3: generate eval report
        eval_report_json_list = self.generate_eval_report(eval_dims_json_list)
        LOGGER.info(f"End: generate evaluation report done.")
        LOGGER.info("-------------------------------------------")
        return {'eval_report_json_list': eval_report_json_list, 'eval_dims_json_list': eval_dims_json_list}

    def eval(self, prompt_answer_list: List[List[Tuple[str, str]]], max_eval_lines: int) -> List[List[dict]]:
        """Evaluate the dataset in multiple dimensions and give specific scores.

        Args:
            prompt_answer_list (List[List[Tuple[str, str]]]): the list of q&a pair from multiple turns,
            the type of single turn is List[Tuple[str, str]].

            max_eval_lines (int): the maximum number of lines to evaluate.

        Returns:
            res (List[List[dict]]): the list of eval results from multiple turns,
            the type of single turn is List[dict].
        """

        eval_dims_json_list = []
        # the q&a dataset from multiple turns.
        for i in range(len(prompt_answer_list)):
            line_num = 0
            one_turn_prompt_answer_list = prompt_answer_list[i]
            one_turn_eval_dims_json_list = []

            # single turn prompt answer list.
            for j in range(len(one_turn_prompt_answer_list)):

                prompt = one_turn_prompt_answer_list[j][0]
                answer = one_turn_prompt_answer_list[j][1]
                if prompt is None or answer is None:
                    break

                line_num += 1
                if line_num > max_eval_lines:
                    break

                if len(prompt) > 2000:
                    prompt = prompt[0:2000]
                if len(answer) > 5000:
                    answer = answer[0:5000]

                version_prompt: ChatPrompt = self.handle_prompt()

                llm: LLM = self.handle_llm()

                chain = version_prompt.as_langchain() | llm.as_langchain() | StrOutputParser()
                res = chain.invoke(input={'prompt': prompt, 'answer': answer})

                dim_score_json = {'line': line_num}
                dimensions = []
                avg_score = 0.0

                try:
                    if res is not None:
                        data = parse_json_markdown(res)
                        dimensions = data['dimensions']
                        # calculate avg score from multiple dimensions.
                        avg_score = sum(data['score'] for data in dimensions)
                except Exception as e:
                    LOGGER.warn(f'except[eval_prompt_answer_from_jsonl]>>>{e}:{res[0]}')
                    continue
                if len(dimensions) > 0:
                    avg_score = avg_score / len(dimensions)
                dim_score_json['avg_score'] = avg_score
                dim_score_json['dimensions'] = dimensions
                LOGGER.info(f"Progress: the turn {i + 1} query line {line_num} has been evaluated successfully.")

                # single line evaluation from multiple dimensions.
                one_turn_eval_dims_json_list.append(dim_score_json)

            eval_dims_json_list.append(one_turn_eval_dims_json_list)
        return eval_dims_json_list

    def handle_prompt(self) -> ChatPrompt:
        """Prompt module processing."""
        profile: dict = self.agent_model.profile

        profile_prompt_model: AgentPromptModel = AgentPromptModel(introduction=profile.get('introduction'),
                                                                  target=profile.get('target'),
                                                                  instruction=profile.get('instruction'))

        # get the prompt by the prompt version
        prompt_version: str = profile.get('prompt_version')
        version_prompt: Prompt = PromptManager().get_instance_obj(prompt_version)

        if version_prompt is None and not profile_prompt_model:
            raise Exception("Either the `prompt_version` or `introduction & target & instruction`"
                            " in agent profile configuration should be provided.")
        if version_prompt:
            version_prompt_model: AgentPromptModel = AgentPromptModel(
                introduction=getattr(version_prompt, 'introduction', ''),
                target=getattr(version_prompt, 'target', ''),
                instruction=getattr(version_prompt, 'instruction', ''))
            profile_prompt_model = profile_prompt_model + version_prompt_model

        return ChatPrompt().build_prompt(profile_prompt_model, ['introduction', 'target', 'instruction'])

    def handle_llm(self) -> LLM:
        """Language model module processing.

        Returns:
            LLM: The language model.
        """
        llm_name = self.agent_model.profile.get('llm_model').get('name')
        llm: LLM = LLMManager().get_instance_obj(component_instance_name=llm_name, new_instance=True)
        llm.set_by_agent_model(**self.agent_model.profile.get('llm_model'))
        return llm

    def generate_eval_report(self, eval_dims_json_list: List[List[dict]]):
        """Integrate multidimensional evaluation scores and generate evaluation report

        Args:
            eval_dims_json_list (List[List[dict]]) : The list of evaluation results from multiple turns,
            the type of single turn is List[dict].

        Returns:
            eval_report_json_list (List[dict]): The list of evaluation report.
        """
        LOGGER.info(f"Start: generate evaluation report.")

        eval_report_json_list = []
        for i in range(0, len(eval_dims_json_list)):
            line_num = 0
            total_avg_score = 0.0
            dim_avg_score = {}
            # single turn eval dim json list.
            one_turn_eval_dims_json_list = eval_dims_json_list[i]
            for j in range(0, len(one_turn_eval_dims_json_list)):
                one_row_eval_dims_json = one_turn_eval_dims_json_list[j]
                line_num += 1

                total_avg_score += one_row_eval_dims_json['avg_score']
                dimensions = one_row_eval_dims_json['dimensions']
                for k in range(0, len(dimensions)):
                    name = dimensions[k]['name']
                    score = dimensions[k]['score']
                    if name in dim_avg_score:
                        dim_avg_score[name] += float(score)
                    else:
                        dim_avg_score[name] = float(score)

            # calculate single turn total avg score and dim avg score.
            for key in dim_avg_score:
                dim_total_score = dim_avg_score[key]
                dim_avg_score[key] = dim_total_score / line_num
            total_avg_score = total_avg_score / line_num

            # generate one turn report.
            one_turn_report = {
                'line_name': f"query turn {i + 1}",
                'total_avg_score': total_avg_score,
                'dim_avg_score': dim_avg_score
            }
            LOGGER.info(f"Progress: turn {i + 1} evaluation report has generated successfully.")
            eval_report_json_list.append(one_turn_report)

        if len(eval_report_json_list) > 1:
            self.generate_total_eval_report(eval_report_json_list)
            LOGGER.info(f"Progress: total evaluation report has generated successfully.")

        # generate excel report
        self.generate_eval_report_excel(eval_report_json_list)
        return eval_report_json_list

    @staticmethod
    def generate_total_eval_report(eval_report_json_list: List[dict]):
        """Generate total evaluation report, integrate and calculate the total evaluation score for each turn.

        Args:
            eval_report_json_list (List[dict]): The list of evaluation report.
        """

        if len(eval_report_json_list) > 1:
            total_avg_score = 0.0
            total_dim_avg_score = {}
            for i in range(len(eval_report_json_list)):
                total_avg_score += eval_report_json_list[i]['total_avg_score']
                dim_avg_score: dict = eval_report_json_list[i]['dim_avg_score']
                for key in dim_avg_score:
                    if key in total_dim_avg_score:
                        total_dim_avg_score[key] += float(dim_avg_score[key])
                    else:
                        total_dim_avg_score[key] = float(dim_avg_score[key])
            total_avg_score = total_avg_score / len(eval_report_json_list)
            for key in total_dim_avg_score:
                total_dim_avg_score[key] = total_dim_avg_score[key] / len(eval_report_json_list)
            report_line_obj = {
                'line_name': 'total avg score',
                'total_avg_score': total_avg_score,
                'dim_avg_score': total_dim_avg_score
            }
            eval_report_json_list.append(report_line_obj)

    @staticmethod
    def generate_eval_results_excel(prompt_answer_list: List[List[Tuple[str, str]]],
                                    eval_dims_json_list: List[List[dict]]):
        """Generate evaluation results in excel format."""

        rows = []
        columns: List[str] = ['Line Number', 'Avg Score', 'Prompt', 'Answer']
        if len(eval_dims_json_list) > 0 and len(eval_dims_json_list[0]) > 0:
            one_row_eval_result = eval_dims_json_list[0][0]
            dims = one_row_eval_result.get('dimensions', [])
            # wrap excel columns
            for dim in dims:
                columns.append(dim['name'] + ' Score')
                columns.append(dim['name'] + ' Negative Point')

            for i in range(len(eval_dims_json_list)):
                one_turn_eval_results = eval_dims_json_list[i]
                one_turn_prompt_answers = prompt_answer_list[i]

                # write for each turn
                for j in range(len(one_turn_eval_results)):
                    one_row_eval_result = one_turn_eval_results[j]
                    one_row_prompt_answer = one_turn_prompt_answers[j]
                    # wrap rows.
                    line_number = one_row_eval_result['line']
                    avg_score = one_row_eval_result['avg_score']
                    dims = one_row_eval_result['dimensions']

                    row = [line_number, avg_score, one_row_prompt_answer[0], one_row_prompt_answer[1]]
                    for dim in dims:
                        row.append(dim['score'])
                        row.append(dim['negative point'])
                    rows.append(row)

                df = pd.DataFrame(rows, columns=columns)

                df.to_excel(f"./data/eval_results_turn_{i + 1}.xlsx", index=False, engine='openpyxl')
            LOGGER.info(f"Progress: generate evaluation detailed results in excel format successfully.")
            LOGGER.info("-------------------------------------------")

    @staticmethod
    def generate_eval_report_excel(eval_report_json_list: List[dict]):
        """Generate excel eval report."""

        rows = []
        columns: List[str] = ['Line Name', 'Total Avg Score']
        dim_avg_scores = eval_report_json_list[0]['dim_avg_score']
        for dim, score in dim_avg_scores.items():
            columns.append(dim + ' Avg Score')
        for item in eval_report_json_list:
            line_name = item['line_name']
            total_avg_score = item['total_avg_score']
            dim_avg_scores = item['dim_avg_score']

            row = [line_name, total_avg_score]
            for dim, score in dim_avg_scores.items():
                row.append(score)
            rows.append(row)

        df = pd.DataFrame(rows, columns=columns)

        df.to_excel("./data/eval_report.xlsx", index=False, engine='openpyxl')

        # tweak column width
        workbook = load_workbook('./data/eval_report.xlsx')
        worksheet = workbook.active
        column_widths = [25, 20] + [20] * (len(columns) - 2)
        for i, column_width in enumerate(column_widths, 1):
            worksheet.column_dimensions[chr(64 + i)].width = column_width
        workbook.save('./data/eval_report.xlsx')
        LOGGER.info(f"Progress: generate evaluation excel file successfully.")
