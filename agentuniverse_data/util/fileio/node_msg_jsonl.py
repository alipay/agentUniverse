# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/14 17:14
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: node_msg_jsonl.py
import json
import os
import sys

from agentuniverse.base.util.logging.logging_util import LOGGER

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

DATA_DIR = 'data/'
os.makedirs(DATA_DIR, exist_ok=True)


class JsonFileOps(object):
    def __init__(self):
        return

    @classmethod
    def is_file_exist(cls, input_file_name, extension='jsonl'):
        infile = DATA_DIR + input_file_name + '.' + extension
        return os.path.exists(infile)

    @classmethod
    def rm_file_if_exist(cls, input_file_name, extension='jsonl'):
        infile = DATA_DIR + input_file_name + '.' + extension
        if os.path.exists(infile):
            os.remove(infile)
        return


class JsonFileWriter(object):
    def __init__(self, output_file_name: str, extension='jsonl'):
        self.outfile_path = DATA_DIR + output_file_name + '.' + extension
        # create directory if not exist
        directory = os.path.dirname(self.outfile_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.outfile_handler = open(self.outfile_path, 'w', encoding='utf-8')

    def write_json_obj(self, json_obj: dict):
        try:
            # Confirm that it's a json string and then write
            # json.loads(json_obj)
            json_line = json.dumps(json_obj, ensure_ascii=False)
            self.outfile_handler.write(json_line.strip() + '\n')
            self.outfile_handler.flush()
        except Exception as e:
            LOGGER.warn(f"except[write_json_obj]>>>{e}:{json_obj}")

        return

    def write_json_obj_list(self, json_obj_list: list):
        for i in range(0, len(json_obj_list)):
            self.write_json_obj(json_obj_list[i])
        return

    def write_json_prompt(self, prompt: str):
        json_obj = {"prompt": prompt}
        self.write_json_obj(json_obj)

    def write_json_prompt_list(self, prompt_list: list):
        for i in range(0, len(prompt_list)):
            self.write_json_prompt(prompt_list[i])

    def write_json_prompt_answer(self, prompt: str, answer: str):
        json_obj = {"prompt": prompt, "answer": answer}
        self.write_json_obj(json_obj)

    def write_json_prompt_answer_list(self, prompt_answer_list: list):
        for i in range(0, len(prompt_answer_list)):
            self.write_json_prompt_answer(prompt_answer_list[i][0], prompt_answer_list[i][1])


class JsonFileReader(object):
    def __init__(self, input_file_name: str, extension='jsonl'):
        self.infile_handler = None
        self.filename = None
        if JsonFileOps.is_file_exist(input_file_name, extension):
            self.filename = input_file_name + '.' + extension
            self.infile_handler = open(DATA_DIR + self.filename, 'r', encoding='utf-8')

    def read_json_obj(self):
        if not self.infile_handler:
            raise Exception(f"None json file to read: {self.filename}")
            return None

        json_line = self.infile_handler.readline()
        if json_line:
            try:
                json_obj = json.loads(json_line.strip())
                return json_obj
            except Exception as e:
                LOGGER.warn(f"except[read_json_line]>>>{e}:{json_line}")
                return json.loads('{}')
        else:
            return None

    def read_json_obj_list(self):
        obj_list = []

        while True:
            obj = self.read_json_obj()
            if obj is None:
                break
            obj_list.append(obj)

        return obj_list

    def read_json_prompt(self):
        json_obj = self.read_json_obj()
        if json_obj is not None:
            return json_obj.get('prompt')
        else:
            return None

    def read_json_prompt_list(self):
        prompts = []
        while True:
            prompt = self.read_json_prompt()
            if prompt is None:
                break
            prompts.append(prompt)

        return prompts

    def read_json_prompt_answer(self):
        json_obj = self.read_json_obj()
        if json_obj is not None:
            prompt = json_obj.get('prompt') if 'prompt' in json_obj else None
            answer = json_obj.get('answer') if 'answer' in json_obj else None
            return prompt, answer
        else:
            return None, None

    def read_json_prompt_answer_list(self):
        prompt_answer_list = []
        while True:
            prompt, answer = self.read_json_prompt_answer()
            if prompt is None:
                break
            prompt_answer_list.append((prompt, answer))

        return prompt_answer_list
