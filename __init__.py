import openai
import re
import os
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"


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
    if(current_timeStamp - min_element[0]>30):
        min_element[0] = current_timeStamp
        heapq.heappush(open_ai_min_heap, min_element)
        return min_element[1]
    else:
        heapq.heappush(open_ai_min_heap, min_element)
        return ""