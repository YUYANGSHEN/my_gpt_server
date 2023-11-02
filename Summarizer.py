import openai
import re
import rolesDict
from openAiKey import *
import random


class SummarizerAndCandidateQuestionGenerator:
    def __init__(self, role,model='text-davinci-003'):
        self.model = model ##模型，基础模型是davinci-003
        self.latest_question = ""
        self.role = role ##存的是一个字典
        self.update_prompt()

    def update_prompt(self):
        self.prompt = (
            f"一个{self.role['role']}AI助手和用户正在进行多轮对话，根据用户提出的问题，给出{self.role['role']}提出的三个新问题。字数不要超过100字\n"
            "问题输出用字符串列表的形式，例如['Question 1','Question 2','Question 3']。\n"
            "例子\n"
            "最新的问题:你为什么认为人工智能是一种积极的力量\n"
            "['能否举出一些例子来说明人工智能如何帮助人类发挥他们的潜力？', '人工智能对人类社会有什么潜在的负面影响吗？', '我们如何能确保人工智能的安全和道德使用？']\n"
            f"最新的问题:{self.latest_question}\n"
        )


    def extract_summary_and_candidate(self, response_message):
        questions_match = re.findall(r"'(.*?)'", response_message)
        if questions_match:
            return questions_match
        else:
            return self.role["initial_questions"]


    def update_summary_and_candidate(self, question):
        self.latest_question = question
        self.update_prompt()
        response = openai.Completion.create(
            model=self.model,
            prompt=self.prompt,
            max_tokens=2000,
            temperature=0.0,
            stream=True,
        )
        response_texts = ''
        for event in response:
            if event.choices[0]['finish_reason'] is None:
                event_text = event.choices[0]['text']
                response_texts += event_text
        questions = self.extract_summary_and_candidate(response_texts)
        return questions

    def reset_role(self, index):
        if index <= 0 or index > 10:
            index = -1
        self.role = roles_dict[index]
        self.latest_question = ""


# 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

def get_summarization(index):
    openai.api_key = get_openAiKey()
    if index <= 0 or index > 10:
        index = -1
    model = SummarizerAndCandidateQuestionGenerator(roles_dict[index])
    question_index = random.randint(0, len(roles_dict[index]["initial_questions"]) - 1)
    return model.update_summary_and_candidate(roles_dict[index]["initial_questions"][question_index])

#
# print(get_summarization(1))