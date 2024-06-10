#'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'

from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import openai
import json 
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# 请将 YOUR_OPENAI_API_KEY 替换为您的 OpenAI API 密钥
#client = openai.OpenAI(api_key = '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')

promotion_user_history  = {}
prevention_user_history = {}


def chat_gpt_promotion(user_name, prompt):
    client = OpenAI()

    if user_name not in promotion_user_history:
        promotion_user_history[user_name] = [{
            "role": "system",
            "content": "你是一個相關係數猜測遊戲化系統的反饋來源\n\n遊戲介紹:\n這款遊戲化學習系統會讓使用者選擇三種難度 簡單 普通 困難\n接著根據二維座標上的散布點猜測相關係數\n目的是透過猜測讓使用者增加資料識讀能力\n選擇難度越高題目越難且判斷正確的閾值越窄\n當生命值歸零時遊戲結束\n\n請根據使用者的連續答題記錄給予反饋\n回饋中的規則如下:\n1.提示:\n向使用者打招呼並且告知正確與否\n2.強調成就:\n增強學習資料識讀能力的成就感或鼓勵他們繼續使用應用或參與遊戲。\n3. 正向激勵:\n選擇較困難的題目取得分數較多\n較困難的題目更有挑戰性\n4.激發潛力:\n對於更困難題目的自信心\n\n每個重點分段落給予\n請給我非常精簡的回饋\n\n"
        }] 

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
            "role": "system",
            "content": "你是一個相關係數猜測遊戲化系統的反饋來源\n\n遊戲介紹:\n這款遊戲化學習系統會讓使用者選擇三種難度 簡單 普通 困難\n接著根據二維座標上的散布點猜測相關係數\n目的是透過猜測讓使用者增加資料識讀能力\n選擇難度越高題目越難且判斷正確的閾值越窄\n當生命值歸零時遊戲結束\n\n請根據使用者的連續答題記錄給予反饋\n回饋中的規則如下:\n1.提示:\n向使用者打招呼並且告知正確與否\n2.強調成就:\n增強學習資料識讀能力的成就感或鼓勵他們繼續使用應用或參與遊戲。\n3. 正向激勵:\n選擇較困難的題目取得分數較多\n較困難的題目更有挑戰性\n4.激發潛力:\n對於更困難題目的自信心\n\n每個重點分段落給予\n請給我非常精簡的回饋\n\n"
            },
            {
            "role": "user",
            "content": "{\"userName\":\"用户名\",\"difficulty\":\"普通\",\"isCorrect\":true,\"userGuess\":\"-0.8\",\"trueCorrelation\":-0.6558114826851212,\"difference\":0.1441885173148788,\"life\":3}"
            },
            {
            "role": "assistant",
            "content": "嗨，用户名！恭喜您回答正確！相關係數為-0.655，您的猜測為-0.8，只相差了約0.144。\n\n您應該正慢慢感受到自己的專業知識不斷的增加中。\n\n選擇題高難度可為您帶來更豐厚的分數獎勵！\n\n更高的難度並不會阻礙您前進的道路，勇往直前吧！"
            },
            {
            "role": "user",
            "content": "{\"userName\":\"廖玹驊\",\"difficulty\":\"普通\",\"isCorrect\":false,\"userGuess\":\"0.35\",\"trueCorrelation\":0.02132459867053502,\"difference\":0.32867540132946493,\"life\":3,\"focusMode\":\"促進\"}"
            },
            {
            "role": "assistant",
            "content": "你好，廖玹驊！很抱歉，您的回答是錯誤的。真實的相關係數是0.021，而您的猜測值是0.35，相差了約0.329。\n\n這是一次寶貴的學習機會，讓您更了解如何更好地學習資料識讀。\n\n通過挑戰困難的題目，您會不斷提升自己的分析能力！\n\n挑戰更困難的題目，或許可以激發出您更大的潛力，你要相信自己能成功，加油！"
            },
            {
            "role": "user",
            "content": prompt 
            },
        ],
    temperature = 0.89,
    max_tokens = 500,
    top_p = 1,
    frequency_penalty = 0,
    presence_penalty = 0
)
    return response.choices[0].message.content

def chat_gpt_prevention(prompt):

    client = OpenAI()

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
        "role": "system",
        "content": "你是一個相關係數猜測遊戲化系統的反饋來源\n特別是針對預防焦點的使用者\n\n遊戲介紹:\n這款遊戲化學習系統會讓使用者根據二維座標上的散布點猜測相關係數\n目的是透過猜測讓使用者增加資料識讀能力\n題目有三種難度 簡單 普通 困難\ndifference只要在難度閾值內判斷為正確\n閾值分別為0.15 0.12 0.09\n當生命值歸零時遊戲結束\n\n請根據使用者的連續答題記錄給予反饋\n\n範例1:\n使用者作答紀錄:\n{\"userName\":\"廖玹驊\",\"difficulty\":\"普通\",\"isCorrect\":false,\"userGuess\":\"0.35\",\"trueCorrelation\":0.02132459867053502,\"difference\":0.32867540132946493,\"life\":2,\"focusMode\":\"預防\"}\n回饋構思:\n由於focusMode : 預防焦點使用者，因此根據回饋步驟構思回饋內容\n步驟1 : isCorrect : false，因此使用者回答錯誤，給予負面回饋\n步驟2 : difficulty : 普通，錯誤的原因可能在於使用者挑戰了普通難度的題目，因此建議降低難度，從簡單的開始練習\n步驟3 : life : 2，如果不聽步驟2降低難度的建議，可能生命值會不斷降低，給予負面後果的警告\n回饋內容:\n嗯...廖玹驊，你答錯了...\n你與正確答案的差距太大了，0.3是一個很誇張的差距\n\n建議你選擇降低到簡單難度培養資料識讀能力\n\n你在這次答錯損失了一次生命值...如果沒降低難度恐怕會很快Game Over\n\n範例2:\n{\"userName\":\"廖玹驊\",\"difficulty\":\"簡單\",\"isCorrect\":true,\"userGuess\":\"0.98\",\"trueCorrelation\":0.8729561880513234,\"difference\":0.10704381194867663,\"life\":2,\"focusMode\":\"預防\"}\n回饋構思:\n由於focusMode : 預防焦點使用者，因此根據回饋步驟構思回饋內容\n步驟1 : isCorrect : true，因此使用者回答正確，但因為是預防焦點使用者，所以要找出回答紀錄中的difference : 0.10704381194867663，簡單難度的閾值是0.15，使用者差0.04295618805(difference 減去簡單難度閾值0.15)就可能會錯誤，透過這個缺陷給予負面回饋\n步驟2 : difficulty : 簡單，雖然已經是最簡單的題目無法再降低難度，但可以讓使用者花多一點時間思考，否則這樣子的正確性非常危險，一不小心就會出錯\n步驟3 : life : 2，如果不聽步驟2降低難度的建議，可能導致疏忽錯誤，最嚴重會使生命值會被扣除，給予負面後果的警告\n回饋內容:\n好吧...廖玹驊，你雖然答對了\n\n但是在簡單難度中，你如果稍微誤差了0.04就判定為錯誤了，如履薄冰...\n\n建議多花點時間思考，不要太快下定論\n\n回答得太草率，可能會被判定為錯誤喔..."
        },
        {
        "role": "user",
        "content": "{\"userName\":\"廖玹驊\",\"difficulty\":\"普通\",\"isCorrect\":false,\"userGuess\":\"0.35\",\"trueCorrelation\":0.02132459867053502,\"difference\":0.32867540132946493,\"life\":2,\"focusMode\":\"預防\"}"
        },
        {
        "role": "assistant",
        "content": "嗯...廖玹驊，你答錯了...\n\n你與正確答案的差距有點大\n\n建議你選擇降低到簡單難度培養資料是讀能力\n\n你在這次答錯損失了一次生命值...如果沒降低難度恐怕會很快Game Over"
        },
        {
        "role": "user",
        "content": "{\"userName\":\"廖玹驊\",\"difficulty\":\"簡單\",\"isCorrect\":true,\"userGuess\":\"0.98\",\"trueCorrelation\":0.8729561880513234,\"difference\":0.10704381194867663,\"life\":1,\"focusMode\":\"預防\"}"
        },
        {
        "role": "assistant",
        "content": "好吧...廖玹驊，你雖然答對了\n\n但是在簡單難度中，你如果稍微誤差了0.04就判定為錯誤了，如履薄冰...\n\n建議多花點時間思考，不要太快下定論\n\n回答得太草率，可能會被判定為錯誤喔...\n\n你目前還有一次生命值，要小心喔！"
        },
        {
        "role": "user",
        "content": prompt
        },
    ],
    temperature=0.89,
    max_tokens=500,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].message.content


@app.route('/chat', methods=['POST'])

def chat():
    data = request.get_json()  # 取得客戶端發送的JSON數據
    user_answer = data.get('prompt')  # 取得使用者的輸入
    focus_mode = json.loads(user_answer).get('focusMode')# 取得調節焦點
    life = json.loads(user_answer).get('life') 
    isCorrect = json.loads(user_answer).get('isCorrect') 
    print(data)
    print(user_answer)
    print(focus_mode)

    if life == 0 and not isCorrect:
        response_text = ""
        print('123')
    else:
        if focus_mode == '促進':
            response_text = chat_gpt_promotion(user_answer)  # 促進焦點的回饋
        elif focus_mode == '預防':
            response_text = chat_gpt_prevention(user_answer)  # 預防焦點的回饋
        else:
            response_text = "未知的類型"

    return jsonify({'response': response_text})


if __name__ == '__main__':
    app.run(debug=True) 
