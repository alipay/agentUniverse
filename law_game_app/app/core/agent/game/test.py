actions = [
    {
        'stage': 1,
        'content': {
            'name': '原告方',
            'action': '陈述'
        }
    },
    {
        'stage': 2,
        'content': {
            'name': '审判员',
            'action': '判断原告方的陈述是否与当前背景有关'
        }
    },
    {
        'stage': 3,
        'content': {
            'name': '被告方',
            'action': '陈述'
        }
    },
    {
        'stage': 4,
        'content': {
            'name': '审判员',
            'action': '判断原告方的陈述是否与当前背景有关'
        }
    },
    {
        'stage': 5,
        'content': {
            'name': '原告方',
            'action': '陈述'
        }
    },
    {
        'stage': 6,
        'content': {
            'name': '法官',
            'action': '向两方提问'
        }
    },
]

# 将列表转换为字典，以 stage 作为 key
actions_dict = {item['stage']: item['content'] for item in actions}

print(actions_dict)
# 现在你可以通过 stage 来获取 content
stage_1_content = actions_dict[1]  # {'name': '原告方', 'action': '陈述'}
stage_6_content = actions_dict[6]  # {'name': '法官', 'action': '向两方提问'}