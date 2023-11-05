import time
import sys


from ChatRobot import *
from Summarizer import *
from flask import Flask, request, jsonify
from openAiKey import *
from rolesDict import *
import openai
app = Flask(__name__)

userChatBot = {}
userSummerizer = {}
userTime = {}
# os.environ["OPENAI_API_KEY"] = "production"
def getChatBot(userId):
    return userChatBot[userId]

def getSummerizer(userId):
    return userSummerizer[userId]

@app.route('/initialization', methods=['POST','GET'])
def initialization():
    if request.method == 'GET':
        userId = request.args.get('userId', None)
    elif request.method == 'POST':
        params = request.json
        userId = params["userId"]
    else:
        return jsonify({'error': 'Wrong method'}), 400
    userChatBot[userId] = ChatBotWithRole()
    userSummerizer[userId] = SummarizerAndCandidateQuestionGenerator(roles_dict[-1])
    userTime[userId] = time.time()
    return jsonify(success=True), 200



@app.route('/choose_role', methods=['POST','GET'])
def choose_role():
    if request.method == 'GET':
        params = request.args
        userId = params.get("userId",None)
        index = int(params.get("index",None))
    elif request.method == 'POST':
        params = request.json
        userId = params["userId"]
        index = int(params["index"])
    else:
        return jsonify({'error': 'Wrong method'}), 400
    chatRobot = getChatBot(userId)
    summarizer = getSummerizer(userId)
    chatRobot.reset_role(index)
    summarizer.reset_role(index)
    return jsonify(success=True), 200


@app.route('/question', methods=['POST','GET'])
def question():
    if request.method == 'GET':
        params = request.args
        userId = params.get("userId",None)
        question = params.get("question",None)
    elif request.method == 'POST':
        params = request.json
        userId = params["userId"]
        question = params["question"]
    else:
        return jsonify({'error': 'Wrong method'}), 400
    print(userChatBot)
    chatModel = userChatBot[userId]
    openai.api_key = get_openAiKey()
    answer = chatModel.user_input(question)
    output = {"answer":answer}
    return jsonify(output)

@app.route('/summarization', methods=['POST','GET'])
def summarization():
    if request.method == 'GET':
        params = request.args
        userId = params.get("userId",None)
        question = params.get("question",None)
    elif request.method == 'POST':
        params = request.json
        userId = params["userId"]
        question = params["question"]
    else:
        return jsonify({'error': 'Wrong method'}), 400
    summarizerModel = userSummerizer[userId]
    openai.api_key = get_openAiKey()
    answer = summarizerModel.update_summary_and_candidate(question)
    output = {"answer":answer}
    return jsonify(output)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345, debug=True, use_reloader=False)