#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time   : 2024/7/24 10:47
# @Author : fluchw
# @Email  : zerozed00@qq.com
# @File   ：test_app.py

import requests
import json
from pprint import pprint

# API接口URL
url = 'http://192.168.0.112:8881/service_run'

# 创建一个包含不同数据的列表
data_list = [
    {
        "service_id": "game_service",
        "params": {
            "user_role": "原告方",
            "user_id": "1984",
            "input": "",
            "cur_node": "a0",
            "background": "李明诉王芳欠款纠纷案。2019年3月，李明借给王芳10万元人民币，约定一年后归还。双方没有签订书面借款合同，但有微信聊天记录为证。到2020年3月归还期限到期后，王芳以各种理由推脱，至今未归还借款。李明多次催促未果，遂向法院提起诉讼，要求王芳归还借款10万元并支付相应的利息。"
        }
    },
    {
        "service_id": "game_service",
        "params": {
            "user_role": "原告方",
            "user_id": "1984",
            "input": "我有半年的聊天记录都可以作证",
            "cur_node": "a1",
        }
    },
    {
        "service_id": "game_service",
        "params": {
            "user_role": "原告方",
            "user_id": "1984",
            "input": "",
            "cur_node": "a2",
        }
    }
]

# 设置请求头
headers = {
    'Content-Type': 'application/json'
}


# 遍历数据列表，对每个数据点发出请求
for data in data_list:
    json_data = json.dumps(data)

    # 发送POST请求
    response = requests.post(url, data=json_data, headers=headers)

    # # 检查响应状态码
    # if response.status_code == 200:
    #     # 请求成功，处理返回的数据
    #     print("请求成功，返回数据:")
    #     pprint(response.json())
    # else:
    #     # 请求失败，打印错误信息
    #     print(f"请求失败，状态码: {response.status_code}")
    # 检查响应状态码
    if response.status_code == 200:
        # 请求成功，处理返回的数据
        print("请求成功，返回数据:")
        pprint(response.json())
    else:
        # 请求失败，打印错误信息
        print(f"请求失败，状态码: {response.status_code}")
