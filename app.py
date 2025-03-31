# import
from flask import Flask, request, jsonify
from flask_cors import CORS
import json 
from openai import OpenAI
import os
from scipy.stats import t

from chat_handlers import (
    chat_gpt_promotion_correlation,
    chat_gpt_prevention_correlation,
    chat_gpt_promotion_pValue,
    chat_gpt_prevention_pValue,
)
from globals import promotion_user_history_pValue, prevention_user_history_pValue, promotion_user_history_correlation, prevention_user_history_correlation
from stats_handlers import handle_ttest

#OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return 'Hello, Vercel with POST!'
    return 'Hello, Vercel!'

##相關係數
@app.route('/chat_correlation', methods=['GET', 'POST'])
def feedback_chat():
    data = request.get_json()  # 取得客戶端發送的JSON數據
    user_answer = data.get('prompt')  # 取得使用者的輸入
    focus_mode = json.loads(user_answer).get('focusMode')# 取得調節焦點
    life = json.loads(user_answer).get('life') 
    isCorrect = json.loads(user_answer).get('isCorrect') 
    user_name = json.loads(user_answer).get('userName') 

    if life == 0 and not isCorrect:
        response_text = ""
        prevention_user_history_correlation.pop(user_name, None)
        promotion_user_history_correlation.pop(user_name, None)
    else:
        if focus_mode == '促進':
            response_text = chat_gpt_promotion_correlation(user_name, user_answer)  # 促進焦點的回饋
        elif focus_mode == '預防':
            response_text = chat_gpt_prevention_correlation(user_name, user_answer)  # 預防焦點的回饋
        else:
            response_text = "未知的類型"

    response = jsonify({'response': response_text})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/chat_pValue', methods=['GET', 'POST'])
def feedback_chat_pValue():
    data = request.get_json()  # 取得客戶端發送的JSON數據
    user_answer = data.get('prompt')  # 取得使用者的輸入
    focus_mode = json.loads(user_answer).get('focusMode')# 取得調節焦點
    life = json.loads(user_answer).get('life') 
    isCorrect = json.loads(user_answer).get('isCorrect') 
    user_name = json.loads(user_answer).get('userName') 
    print(user_answer)
    if life == 0 and not isCorrect:
        response_text = ""
        promotion_user_history_pValue.pop(user_name, None)
        prevention_user_history_pValue.pop(user_name, None)
    else:
        if focus_mode == '促進':
            response_text = chat_gpt_promotion_pValue(user_name, user_answer)  # 促進焦點的回饋
        elif focus_mode == '預防':
            response_text = chat_gpt_prevention_pValue(user_name, user_answer)  # 預防焦點的回饋
        else:
            response_text = "未知的類型"

    response = jsonify({'response': response_text})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/ttest', methods=['GET', 'POST'])
def handle_tvalue():
    return handle_ttest(request)

if __name__ == '__main__':
    app.run(debug=True)