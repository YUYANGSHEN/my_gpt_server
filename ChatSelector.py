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