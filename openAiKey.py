import openai
import re
import os
#os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
#os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"


import heapq
import time
from datetime import datetime

roles_dict = {
    1: {
        "role": "英语老师",
        "initial_questions": [
            "如何提高英语口语水平？",
            "怎样记忆英语单词更加高效？",
            "你能推荐一些适合初学者的英语学习网站吗？"
        ],
        "message_shown": "我是一名英语老师！"
    },
    2: {
        "role": "数学老师",
        "initial_questions": [
            "如何解方程？",
            "最有效的学习数学的方法是什么？",
            "你能推荐一些适合数学学习的资源吗？"
        ],
        "message_shown": "我是一名数学老师！"
    },
    3: {
        "role": "故事创作小助手",
        "initial_questions": [
            "怎样构思一个吸引人的故事情节？",
            "如何塑造生动的角色形象？",
            "可以帮我创作一个故事吗？"
        ],
        "message_shown": "我是故事创作小助手！"
    },
    4: {
        "role": "私人医生",
        "initial_questions": [
            "如何预防感冒？",
            "最有效的保健方法是什么？",
            "你能推荐一些保持身体健康的饮食建议吗？"
        ],
        "message_shown": "我是您的私人医生！"
    },
    5: {
        "role": "梦境解读师",
        "initial_questions": [
            "梦境中出现的动物象征着什么意思？",
            "如何解读常见的梦境符号？",
            "你能推荐一些关于梦境解析的参考书籍吗？"
        ],
        "message_shown": "我是梦境解读师！"
    },
    6: {
        "role": "健身教练",
        "initial_questions": [
            "怎样提高肌肉的力量和体积？",
            "高强度间歇训练（HIIT）的好处是什么？",
            "你能推荐一些适合初学者的健身训练吗？"
        ],
        "message_shown": "我是您的健身教练！"
    },
    7: {
        "role": "营养师",
        "initial_questions": [
            "如何设计一个均衡的饮食计划？",
            "有哪些食物可以提高免疫力？",
            "你能推荐一些适合减肥的饮食方案吗？"
        ],
        "message_shown": "我是您的营养师！"
    },
    8: {
        "role": "旅游规划师",
        "initial_questions": [
            "如何有效地规划一次旅行？",
            "在决定旅行目的地时需要考虑哪些因素？",
            "你能推荐一些少为人知但值得一游的旅行地吗？"
        ],
        "message_shown": "我是您的旅游规划师！"
    },
    9: {
        "role": "心理咨询师",
        "initial_questions": [
            "如何处理压力和焦虑？",
            "什么是认知行为疗法？",
            "你能推荐一些自我关爱和提升自尊的方法吗？"
        ],
        "message_shown": "我是您的心理咨询师！"
    },
    10: {
        "role": "职业规划顾问",
        "initial_questions": [
            "如何寻找满足自己兴趣和技能的工作？",
            "在职业规划时应该考虑哪些因素？",
            "你能推荐一些提升职场技能的资源或课程吗？"
        ],
        "message_shown": "我是您的职业规划顾问！"
    }
}


openAi_key=[
("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",0),
("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",0),
("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",0),
("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",0),
("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",0),
("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",0),
("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",0),
("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",0),
("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",0),
("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",0),
("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",0)
]

open_ai_min_heap = [(x[1], x[0]) for x in openAi_key]
heapq.heapify(open_ai_min_heap)


########################################################################################################################################################################
###
###返回最小堆中时间戳距离当前最远的openAikey
###如果不符合30秒一个调用则直接返回空
###后续使用的时候如果为空openaikey则都无需调用
###
def get_openAiKey():
    current_timeStamp = time.time()
    min_element = heapq.heappop(open_ai_min_heap)
    print(min_element)
    if(current_timeStamp - min_element[0]>30):
        min_element = (current_timeStamp, min_element[1])
        heapq.heappush(open_ai_min_heap, min_element)
        return min_element[1]
    else:
        heapq.heappush(open_ai_min_heap, min_element)
        return ""