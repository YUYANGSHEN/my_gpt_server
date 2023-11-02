import openai
import rolesDict
from openAiKey import *


class ChatBotWithRole:
    def __init__(self, role="人工智能机器人", model="gpt-3.5-turbo"):
        self.role = role
        self.model = model
        self.messages = []
        self.system_message = self.initialize_system_message()

    def initialize_system_message(self):
        system_message = {
            "role": "system",
            "content": f"你是一名{self.role}。不符合你身份的专业的问题，请回答'我是一名{self.role}，我无法回答您提出的问题'。 "
        }
        return system_message

    def user_input(self, question):
        user_message = {
            "role": "user",
            "content": question
        }
        self.messages.append(user_message)
        if len(self.messages) > 5:
            self.messages = self.messages[-5:]
        return self.generate_response()

    def generate_response(self):
        message_input = [self.system_message]
        message_input.append(self.messages)
        print(message_input)
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            stream=True,
            max_tokens=2000,
        )
        response_texts = ''
        for event in completion:
            if len(event.choices[0]['delta']) == 0:
                break
            event_text = event.choices[0]['delta']['content']
            response_texts += event_text
            print(event_text, end="")

        assistant_answer = {
            "role": 'assistant',
            "content": response_texts
        }

        self.messages.append(assistant_answer)

        return response_texts



    def reset_role(self,index):
        if index <= 0 or index > 10:
            index = -1
        self.role = roles_dict[index]["role"]
        self.system_message = self.initialize_system_message()
        self.messages = []

def get_response(index):
    openai.api_key = get_openAiKey()
    model = ChatBotWithRole()
    return model.user_input("如何提高英语水平")


# print(get_response(1))