import requests


url1 = 'http://127.0.0.1:12345/initialization' ##机器人初始化
url2 = 'http://127.0.0.1:12345/choose_role' ##选取角色
url3 = 'http://127.0.0.1:12345/question'  ##输入问题，返回答案
url4 = 'http://127.0.0.1:12345/summarization' ##总结新的问题
# 请求的查询参数
params = {
    'userId': 'alice',  # 更改为你需要查询的用户名
    'index': 1,
    'question':"water中文怎么说"
}

# 发送GET请求
response = requests.post(url1, json=params)
response = requests.get(url2, params)
response = requests.get(url3, params)
print(response.json())
response = requests.get(url4, params)
print(response.json())