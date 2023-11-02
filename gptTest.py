import openai
import re
import os
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
openai.api_key = "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"


class SummarizerAndCandidateQuestionGenerator:
    def __init__(self, role,model='text-davinci-003', summary_max_tokens=100):
        self.model = model
        self.current_summary = '无先前对话'
        self.summary_max_tokens = summary_max_tokens
        self.latest_conversation = []
        self.role = role
        self.update_prompt()

    def update_prompt(self):
        if len(self.current_summary) > self.summary_max_tokens:
            self.current_summary = self.current_summary[:self.summary_max_tokens]
        print("")
        self.prompt = (
            f"一个AI助手和用户正在进行多轮对话，根据提供的之前对话摘要和最新一轮对话内容，生成新的摘要并预测接下来{self.role}给出的三个新的专业问题。输出为json格式\n"
            f"新的摘要字符数不要超过设定的上限 {self.summary_max_tokens} 个token\n"
            "问题输出用字符串列表的形式，例如['Question 1','Question 2','Question 3']。\n\n"
            "例子\n"
            "当前摘要: 用户询问AI对人工智能的看法。AI认为人工智能是一种积极的力量。\n"
            "最新一轮对话：\n"
            "[{'role': 'user', 'content': '你为什么认为人工智能是一种积极的力量？'},"
            "{'role': 'assistant', 'content': '因为人工智能将帮助人类发挥他们的全部潜力。'}]\n"
            "输出:\n"
            "{\n"
            "'新摘要': '用户进一步询问为什么AI认为人工智能是积极的力量，AI解释称人工智能有助于发挥人类的全部潜力。',\n"
            "'候选问题': ['你能给我一些具体的例子来说明人工智能如何帮助人类发挥他们的潜力吗？', '人工智能对人类社会有什么潜在的负面影响吗？', '我们如何能确保人工智能的安全和道德使用？']\n"
            "}\n\n"
            f"当前摘要: {self.current_summary[:self.summary_max_tokens]}\n"
            f"最新一轮对话: {self.latest_conversation}\n"
        )
        print(self.prompt)
    # def load_first_conversation(self, conversation):
    #     self.latest_conversation = conversation
    #     self.update_prompt()

    def extract_summary_and_candidate(self, response_message):
        print(11111111111111111111111)
        print(response_message)
        summary_match = re.search(r"'新摘要': '([^']*)'", response_message)
        if summary_match:
            summary = summary_match.group(1)

        questions_match = re.findall(r"'候选问题': \[([^]]*)\]", response_message)
        if questions_match:
            questions = [question.strip(" '") for question in questions_match[0].split(',')]
        else:
            questions = None

        return summary, questions

    def update_summary_and_candidate(self, conversation):
        self.latest_conversation = conversation
        self.update_prompt()
        # print(self.prompt)
        self.prompt
        print(self.prompt)
        response = openai.Completion.create(
            model="text-davinci-003",
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
                # print(event_text, end="")
        # print("test")
        # print(response_texts)
        summary, questions = self.extract_summary_and_candidate(response_texts)

        if summary:
            self.current_summary = summary
        return questions


class ChatBotWithRole:
    def __init__(self, role="AI assistent", model="gpt-3.5-turbo", initial_system_message=None, initial_questions=None):
        self.role = role
        self.model = model
        self.messages = []
        self.summarizer = SummarizerAndCandidateQuestionGenerator(role)
        self.initial_system_message = initial_system_message
        self.candidate_questions = initial_questions or []
        self.initialize_conversation()

    def initialize_conversation(self):
        if self.initial_system_message is not None:
            system_message = {
                "role": "system",
                "content": self.initial_system_message
            }
        else:
            system_message = {
                "role": "system",
                "content": f"你是一名 {self.role}。 不符合你身份或者其他专业的问题，请回答'我不知道'。 "
            }
        self.messages.append(system_message)
        # self.summarizer.load_first_conversation([system_message])

    def user_input(self, user_content):
        if len(self.messages) > 1:
            self.update_system_message()
        user_message = {
            "role": "user",
            "content": user_content
        }
        self.messages.append(user_message)

        return self.generate_response()

    def generate_response(self):
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            stream=True,
            max_tokens=500,
        )
        response_texts = ''
        # print(completion.choices[0]["message"]["content"])
        for event in completion:
            if len(event.choices[0]['delta']) == 0:
                break
            event_text = event.choices[0]['delta']['content']
            response_texts += event_text
            print(event_text, end="")

        assistant_message = {
            "role": 'assistant',
            "content": response_texts
        }

        self.messages.append(assistant_message)

        # Update the summarizer with the latest conversation
        candidate_questions = self.summarizer.update_summary_and_candidate(self.messages[-2:])

        return candidate_questions

    def get_current_summary(self):
        return self.summarizer.current_summary

    def update_system_message(self):
        print(self.messages[0]['content'])
        new_system_message = {
            "role": "system",
            "content": f"{self.messages[0]['content']} 。 之前对话的摘要是 {self.get_current_summary()}."
        }
        self.messages = [new_system_message]


class ChatBotRoleSelector:
    MAX_INPUT_LENGTH = 50

    def __init__(self, role_dict):
        if role_dict is None:
            raise ValueError("role_dict cannot be None")
        else:
            self.role_dict = role_dict

    def safe_input(self, prompt):
        user_input = input(prompt)[:self.MAX_INPUT_LENGTH].strip()
        print(user_input)
        return user_input

    def initial_select_role(self):
        # roles = self.role_dict.keys()

        while True:
            try:
                print("请选择您需要的功能：")
                for num, role in self.role_dict.items():
                    print(f"{num}. {role['role']}")
                selected_role = int(self.safe_input("请输入对应的编号: "))
                if selected_role in self.role_dict.keys():
                    return selected_role
                else:
                    print("请输入有效的编号！")
            except ValueError:
                print("请输入一个有效的整数编号！")


def main():
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

    selector = ChatBotRoleSelector(role_dict=roles_dict)

    selected_role = selector.initial_select_role()

    selected_role_info = roles_dict.get(selected_role)

    role = selected_role_info["role"]

    initial_questions = selected_role_info["initial_questions"]

    message_shown = selected_role_info["message_shown"]
    chatbot = ChatBotWithRole(role, initial_questions=initial_questions)

    # Print welcome message
    print(message_shown)

    # Print the initial questions
    print("例如你可以问我这些问题，或者提出你自己的问题:")
    for i, question in enumerate(chatbot.candidate_questions):
        print(f"{i + 1}. {question}")

    candidate_questions = chatbot.candidate_questions
    # print(candidate_questions)
    # Loop to continue the conversation as long as the user wants
    while True:
        # Get input from user
        user_input = input("User: ")

        # Break the loop if the user types 'quit'
        if user_input.lower() == "quit" or user_input.lower() == "exit":
            break

        # If the user input is a number and there are candidate questions,
        # use the corresponding candidate question as the user input
        if user_input.isdigit() and candidate_questions:
            if int(user_input) >= 1 and int(user_input) <= len(candidate_questions):
                user_input = candidate_questions[int(user_input) - 1]
            else:
                print("请输入正确的数字 (1-3) 或者自己的问题")
                continue

        print(f"\n{'=' * 100} \n 你的问题是: {user_input}\n{'=' * 100}")
        # Generate response from the chatbot
        candidate_questions = chatbot.user_input(user_input)

        # Print the candidate questions
        if candidate_questions:
            print(f"\n{'=' * 100} \n \n你可能要问:")
            for i, question in enumerate(candidate_questions):
                print(f"{i + 1}. {question}")


if __name__ == "__main__":
    main()