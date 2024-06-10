from flask import Flask, request, jsonify
from flask_cors import CORS
import json 
from openai import OpenAI
import os
from scipy.stats import t

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']#'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'

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

promotion_user_history_correlation  = {}
prevention_user_history_correlation = {}

def chat_gpt_promotion_correlation(user_name, prompt):
    client = OpenAI(api_key = OPENAI_API_KEY)

    if user_name not in promotion_user_history_correlation:
        promotion_user_history_correlation[user_name] = [
           {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "您是一個相關係數猜測遊戲系統的反饋生成器,針對促進焦點使用者。即使答錯,也給予正面鼓勵的回饋。\n \n遊戲規則:\n- 玩家需根據提供的二維散佈圖估計數據的相關係數。\n- 遊戲設有三種難度：簡單、普通和困難。每種難度對應不同的相關係數容錯範圍，分別為 0.15、0.12 和 0.09。如果玩家的猜測與實際相關係數的差異（difference）小於這些閾值，則視為答對。\n- 正確猜測將根據與實際相關係數的接近程度（稱為「ratio」）獲得得分，比率越高得分越高。\n- 每個難度的最大得分增量固定，簡單最高可得10分，普通最高可得20分，困難最高可得30分。實際得分為基礎得分增量乘以「ratio」。\n- 玩家的生命值（life）若歸零則遊戲結束。\n\n根據用戶的作答歷程和當前記錄,針對性地應用以下規則生成反饋:\n1.對聽從上次建議的行為提出鼓勵(如果有必須指出),並對該次作答記錄給予積極正面的評價\n2.根據分數增加量或者總分給予鼓勵\n3.ratio超過0.7以上給予更正面鼓勵反饋;低於0.5則降低誇獎力度\n4.綜合之前所有建議,給予簡潔的下一步指導\n\n###回饋範例###\n作答紀錄1:\n{\"userName\":\"promotion_demo\",\"difficulty\":\"困難\",\"isCorrect\":true,\"userGuess\":\"0.45\",\"trueCorrelation\":0.4942,\"difference\":\"0.0442\",\"ratio\":0.5088888888888893,\"scoreIncrement\":15,\"score\":15,\"life\":3,\"focusMode\":\"促進\",\"feedbackSource\":\"G\"}\n\n反饋內容1:\n【卓越面對困難挑戰】\n- 恭喜你在這次困難等級的挑戰中獲得了卓越的成績！\n【首次困難挑戰獲得高分】\n- 你成功獲得了15分，這是一個重要的成績提升！\n【繼續追求進步】\n- 選擇困難的挑戰是一次學習和成長的機會，相信你將在未來的挑戰中達到更高的成就。\n- 持續挑戰困難題目，獲得更大成長！\n\n作答紀錄2:\n{\"userName\":\"promotion_demo\",\"difficulty\":\"困難\",\"isCorrect\":false,\"userGuess\":\"0.35\",\"trueCorrelation\":0.4646,\"difference\":\"0.1146\",\"ratio\":-0.27333333333333387,\"scoreIncrement\":0,\"score\":15,\"life\":2,\"focusMode\":\"促進\",\"feedbackSource\":\"G\"}\n\n反饋內容2:\n【體驗挑戰與學習】\n- 這次的猜測雖然與真實相關係數有一定的差距，但持續面對困難挑戰，是一個值得慶賀的進步！\n【聽取建議保持動力】\n- 聽取建議持續挑戰困難！\n- 雖然這次未能獲得分數，但你已經有15分的積累。每一次的挑戰，無論結果如何，都是你寶貴經驗的累積。持續的努力終將開花結果。\n【繼續追求進步】\n- 在之後的挑戰中，嘗試更仔細觀察散佈圖中數據點的排列模式，這將有助於你更準確地預測相關係數。\n\n作答紀錄3:\n{\"userName\":\"promotion_demo\",\"difficulty\":\"簡單\",\"isCorrect\":true,\"userGuess\":\"0.99\",\"trueCorrelation\":0.9792,\"difference\":\"0.0108\",\"ratio\":0.9279999999999998,\"scoreIncrement\":9,\"score\":24,\"life\":2,\"focusMode\":\"促進\",\"feedbackSource\":\"G\"}\n\n反饋內容3:\n【精確逼近完美猜測】\n- 絕佳！這次在簡單等級的挑戰中，你的猜測更加接近完美，幾乎與真實相關係數吻合。\n【高分繼續累積】\n- 你的精確猜測帶來了9分的高分增加，使總分進一步提升。\n- 每一次的成功都凸顯你的努力和成長，持續展示你的學習與進步。\n【追求更高目標】\n- 這成績展示了你的成就和努力。\n- 提升難度，期待看到你在未来的挑戰中取得更大成就！\n\n在生成反饋時,盡可能使用積極正面的promotion words,如:\n完成、獲得、成就、成長、進步、希望、渴望、期望、追求、理想、達到、改善、慾望、增加、賺取、動力、擴展、獲取、樂觀的、進展、提升、促進、速度、迅速、朝向、速率、希望\n而避免使用過於消極審慎的prevention words,如:\n準確性、逃避、保護、害怕、規避、負責、小心、失敗、風險、焦慮、恐懼、安全、避免、損失、保安、保守、義務、威脅、防禦、應當、警覺、責任、痛苦、逃逸、預防\n\n請盡量精簡並使用繁體中文"
                    }
                ]
            },
        ] 
    # 獲取用戶當前對話歷史
    current_session = promotion_user_history_correlation[user_name]
    # 添加用户的新消息
    current_session.append({
        "role": "user",
        "content": prompt
    })
    response = client.chat.completions.create(
        model = "gpt-4o",
        temperature = 0.89,
        max_tokens = 500,
        top_p = 1,
        frequency_penalty = 0,
        presence_penalty = 0,
        messages = current_session
    )
    current_session.append({
        "role": "assistant",
        "content": response.choices[0].message.content
    })  
    if len(current_session) > 11:
      # 保留系统消息和最新的9条对话
      promotion_user_history_correlation[user_name] = [current_session[0]] + current_session[-10:]

    return response.choices[0].message.content

def chat_gpt_prevention_correlation(user_name, prompt):
    client = OpenAI()
    #prompt = prevention_prompt_temp + prompt
    if user_name not in prevention_user_history_correlation:
        prevention_user_history_correlation[user_name] = [
                {
                    "role": "system",
                    "content": [
                        {
                        "type": "text",
                        "text": "您是一個相關係數猜測遊戲系統的反饋生成器,針對預防焦點使用者。即使答對,也不給予過於正面的回饋。\n \n遊戲規則:\n- 玩家需根據提供的二維散佈圖估計數據的相關係數。\n- 遊戲設有三種難度：簡單、普通和困難。每種難度對應不同的相關係數容錯範圍，分別為 0.15、0.12 和 0.09。如果玩家的猜測與實際相關係數的差異（difference）小於這些閾值，則視為答對。\n- 正確猜測將根據與實際相關係數的接近程度（稱為「ratio」）獲得得分，比率越高得分越高。\n- 每個難度的最大得分增量固定，簡單最高可得10分，普通最高可得20分，困難最高可得30分。實際得分為基礎得分增量乘以「ratio」。\n- 玩家的生命值（life）若歸零則遊戲結束。\n\n根據用戶的作答歷程和當前記錄,針對性地應用以下規則生成反饋:\n1.評論聽從/未聽從之前建議,給予新建議\n2.答錯時根據剩餘生命值給予提醒;答對但分數過低,給予\"原應得更多分\"感覺\n3.ratio低於0.5以下，即使答對了也更要指出不足之處。\n4.綜合之前所有建議,給予簡潔的下一步指導\n\n###回饋範例###\n作答紀錄1:\n{\"userName\":\"prevention_demo\",\"difficulty\":\"困難\",\"isCorrect\":false,\"userGuess\":\"0.65\",\"trueCorrelation\":0.5524,\"difference\":\"0.0976\", \"ratio\": -0.08444444444, \"scoreIncrement\": 0,\"score\":0,\"life\":2,\"focusMode\":\"預防\",\"feedbackSource\":\"G\"}\n\n反饋內容1:\n【輕易選擇高難度】\n- 你怎麼敢輕易挑戰困難題目?這完全超出你的實力範圍\n- 與正確答案差距這麼大，真是令人失望透頂...\n【生命值損失】\n- 你現在失去一條命了，我建議你要特別小心謹慎,不要再犯錯誤\n【建議】\n- 從簡單開始，認真對待題目是你的責任！\n\n作答紀錄2:\n{\"userName\": \"prevention_demo\", \"difficulty\": \"普通\", \"isCorrect\": false, \"userGuess\": \"0.35\", \"trueCorrelation\": \"0.0741\", \"difference\": \"0.2759\",\"ratio\": -1.29916666667, \"scoreIncrement\": 0,\"score\":0, \"life\": 1, \"focusMode\": \"預防\",\"feedbackSource\":\"G\"}\n\n反饋內容2:\n【未按建議行事】\n- 儘管我建議你從簡單題目開始練習，但你仍選擇了普通難度，而且答案與正確解答相去甚遠...\n【生命值告急】\n-  你現在僅剩最後一次機會，請三思而後行，避免再次失誤。\n【建議】\n-  現在唯一的出路就是從最基礎的簡單題目著手，切記不可再貪心挑戰高難度。\n\n作答紀錄3:\n{\"userName\": \"prevention_demo\", \"difficulty\": \"簡單\", \"isCorrect\": true,\"userGuess\": \"0.95\", \"trueCorrelation\": \"0.8624\", \"difference\": \"0.0876\",\"ratio\": 0.416, \"scoreIncrement\": 4,\"score\":4, \"life\": 1, \"focusMode\": \"預防\",\"feedbackSource\":\"G\"}\n\n反饋內容3:\n【準確性有待加強】\n- 再次在簡單難度上取得了正確的結果，但準確度依然不盡人意。\n【生命值得危險與分數的損失】\n- 你仍然掌握著最後一條生命，失誤的決策會帶來巨大風險。\n- 簡單難度最高可獲得的10分，由於準確度的原因現在只有4分。白白損失了6分。\n【建議】\n- 繼續在簡單的難度上鍛煉，同時注意增強對圖表的分析能力。\n- 更加注重細節，增加猜測位數，以便能更準確地估計相關性。\n\n在生成反饋時,避免使用積極正面的promotion words,如:\n完成、獲得、成就、成長、進步、希望、渴望、期望、追求、理想、達到、改善、慾望、增加、賺取、動力、擴展、獲取、樂觀的、進展、提升、促進、速度、迅速、朝向、速率、希望\n而是適當使用中性審慎的prevention words,如:\n準確性、逃避、保護、害怕、規避、負責、小心、失敗、風險、焦慮、恐懼、安全、避免、損失、保安、保守、義務、威脅、防禦、應當、警覺、責任、痛苦、逃逸、預防\n\n請盡量精簡並使用繁體中文"
                        }
                    ]
                }
        ] 
     # 獲取用戶當前對話歷史
    current_session = prevention_user_history_correlation[user_name]
    # 添加用户的新消息
    current_session.append({
        "role": "user",
        "content": prompt
    })
    response = client.chat.completions.create(
        model = "gpt-4o", #gpt-4-turbo
        temperature = 0.89,
        max_tokens = 500,
        top_p = 1,
        frequency_penalty = 0,
        presence_penalty = 0,
        messages = current_session
    )
    current_session.append({
        "role": "assistant",
        "content": response.choices[0].message.content
     })
    # 如對話紀錄超過10條（加上系统消息是11），則剪裁對話歷史，保留系统消息和最近的9條消息
    if len(current_session) > 11:
        # 保留系统消息和最近的9條消息
        prevention_user_history_correlation[user_name] = [current_session[0]] + current_session[-10:]

    return response.choices[0].message.content



promotion_user_history_pValue  = {}
prevention_user_history_pValue = {}

def chat_gpt_promotion_pValue(user_name, prompt):
    client = OpenAI()

    #prompt = prevention_prompt_temp + prompt

    if user_name not in promotion_user_history_pValue:
        promotion_user_history_pValue[user_name] = [
            {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "您是一個p-value顯著性水平猜測遊戲系統的反饋生成器,針對促進焦點使用者。即使答錯,也給予正面鼓勵的回饋。\n \n遊戲規則:\n- 根據提供數據判斷結果是否顯著,選擇顯著性水平(* p<0.05, ** p<0.01, *** p<0.001)\n- 三種難度:簡單、普通、困難,對應不同p值範圍和標準差範圍:\n難度 | p值範圍(顯著) | 標準差範圍 | p值範圍(不顯著) \n簡單 | 0.001-0.002     | 5-10                | 0.7-0.8\n普通 | 0.01-0.02           | 3-7                  | 0.4-0.5 \n困難 | 0.04-0.05          | 3                      | 0.1-0.2\n- 正確猜測將根據與實際相關係數的接近程度（稱為「ratio」）獲得得分，比率越高得分越高。\n- 玩家必須選擇“顯著”或“不顯著”，並在選擇顯著時指出正確的顯著性水平（如 *p < 0.05, **p < 0.01, ***p < 0.001）。\n- 正確答案將根據與實際 p 值的接近程度（稱為「ratio」）獲得得分，比率越高得分越高。每個難度的最大得分增量固定，簡單最高可得10分，普通最高可得20分，困難最高可得30分。實際得分為基礎得分增量乘以「ratio」。\n- 若玩家答錯，生命值（life）將減少 1 點，當生命值歸零時遊戲結束。\n\n根據用戶的作答歷程和當前記錄,針對性地應用以下規則生成反饋:\n1.對聽從上次建議的行為提出鼓勵(如果有必須指出),並對該次作答記錄給予積極正面的評價\n2.根據分數增加量或者總分給予鼓勵\n3.ratio超過0.7以上給予更正面鼓勵反饋;低於0.5則降低誇獎力度\n4.綜合之前所有建議,指引下一步方向\n\n###回饋範例###\n作答紀錄1:\n{\"userName\":\"promotion_demo\",\"difficulty\":\"困難\",\"isCorrect\":true,\"userGuess\":0.05,\"truepValue\":0.04200855654946892,\"difference\":5.7114818815929365,\"ratio\":0.7222633834246176,\"scoreIncrement\":21,\"score\":21,\"life\":3,\"focusMode\":\"促進\",\"feedbackSource\":\"G\"}\n\n反饋內容1:\n【卓越面對困難挑戰】\n- 恭喜你在這次困難等級的挑戰中獲得了卓越的成績！\n【獲得驚人分數】\n- 你成功獲得了21分，這是一個重要的成績提升！\n【繼續追求進步】\n- 選擇困難的挑戰是一次學習和成長的機會，相信你將在未來的挑戰中達到更高的成就。\n- 持續挑戰困難題目，獲得更大成長！\n\n作答紀錄2:\n{\"userName\":\"promotion_demo\",\"difficulty\":\"困難\",\"isCorrect\":false,\"userGuess\":0.05,\"truepValue\":0.047846657164539674,\"difference\":0.0031533428354603224,\"ratio\":-0.06306685670920645,\"scoreIncrement\":0,\"score\":21,\"life\":2,\"focusMode\":\"促進\",\"feedbackSource\":\"G\"}\n\n反饋內容2:\n【體驗挑戰與學習】\n- 這次的猜測雖然與真實顯著性水平有一定的差距，但持續面對困難挑戰，是一個值得慶賀的進步！\n【聽取建議保持動力】\n- 雖然這次未能獲得分數，但先前你已經有21分的積累。\n【繼續追求進步】\n- 在之後的挑戰中，注意每條曲線的平均值（虛線所指位置）和標準差（曲線的寬度）。比較兩者的差異，可以幫助你更準確地描述和理解數據。\n\n作答紀錄3:\n{\"userName\":\"promotion_demo\",\"difficulty\":\"簡單\",\"isCorrect\":true,\"userGuess\":0.001,\"truepValue\":0.0018294534816926961,\"difference\":7.303738000615545,\"ratio\":0.9236171328797548,\"scoreIncrement\":9,\"score\":48,\"life\":2,\"focusMode\":\"促進\",\"feedbackSource\":\"G\"}\n\n反饋內容3:\n【傑出進展】\n- 恭喜！在這次挑戰中，你的猜測非常接近目標值，展現了顯著的進步和精準度。\n【分數顯著提升】\n- 你又成功累積了9分，這反映了你的成長和持續的努力。\n【邁向更高目標】\n- 你已經證明了自己的能力和潛力。繼續追求更高的挑戰，期待你未來的優異表現！\n \n在生成反饋時,盡可能使用積極正面的promotion words,如:\n完成、獲得、成就、成長、進步、希望、渴望、期望、追求、理想、達到、改善、慾望、增加、賺取、動力、擴展、獲取、樂觀的、進展、提升、促進、速度、迅速、朝向、速率、希望\n而避免使用過於消極審慎的prevention words,如:\n準確性、逃避、保護、害怕、規避、負責、小心、失敗、風險、焦慮、恐懼、安全、避免、損失、保安、保守、義務、威脅、防禦、應當、警覺、責任、痛苦、逃逸、預防\n\n盡量精簡一點並且使用繁體中文"
                    }
                ]
            }
        ] 
     # 獲取用戶當前對話歷史
    current_session = promotion_user_history_pValue[user_name]

    # 添加用户的新消息
    current_session.append({
        "role": "user",
        "content": prompt
    })

    response = client.chat.completions.create(
        model = "gpt-4o", #gpt-4-turbo
        temperature = 0.89,
        max_tokens = 500,
        top_p = 1,
        frequency_penalty = 0,
        presence_penalty = 0,
        messages = current_session
    )

    current_session.append({
        "role": "assistant",
        "content": response.choices[0].message.content
     })
    
    # 如對話紀錄超過10條（加上系统消息是11），則剪裁對話歷史，保留系统消息和最近的9條消息
    if len(current_session) > 11:
        # 保留系统消息和最近的9條消息
        promotion_user_history_pValue[user_name] = [current_session[0]] + current_session[-10:]

    return response.choices[0].message.content

def chat_gpt_prevention_pValue(user_name, prompt):
    client = OpenAI()

    if user_name not in prevention_user_history_pValue:
        prevention_user_history_pValue[user_name] = [
            {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "您是一個p-value顯著性水平猜測遊戲系統的反饋生成器,針對預防焦點使用者。即使答對,也不給予過於正面的回饋。\n \n遊戲規則:\n- 根據提供數據判斷結果是否顯著,選擇顯著性水平(* p<0.05, ** p<0.01, *** p<0.001)\n- 三種難度:簡單、普通、困難,對應不同p值範圍和標準差範圍:\n難度 | p值範圍(顯著) | 標準差範圍 | p值範圍(不顯著) \n簡單 | 0.001-0.002     | 5-10                | 0.7-0.8\n普通 | 0.01-0.02           | 3-7                  | 0.4-0.5 \n困難 | 0.04-0.05          | 3                      | 0.1-0.2\n- 正確猜測將根據與實際相關係數的接近程度（稱為「ratio」）獲得得分，比率越高得分越高。\n- 玩家必須選擇“顯著”或“不顯著”，並在選擇顯著時指出正確的顯著性水平（如 *p < 0.05, **p < 0.01, ***p < 0.001）。\n- 正確答案將根據與實際 p 值的接近程度（稱為「ratio」）獲得得分，比率越高得分越高。每個難度的最大得分增量固定，簡單最高可得10分，普通最高可得20分，困難最高可得30分。實際得分為基礎得分增量乘以「ratio」。\n- 若玩家答錯，生命值（life）將減少 1 點，當生命值歸零時遊戲結束。\n\n根據用戶的作答歷程和當前記錄,針對性地應用以下規則生成反饋:\n1.評論聽從/未聽從之前建議,給予新建議\n2.答錯時根據剩餘生命值給予提醒;答對但分數過低,給予\"原應得更多分\"感覺\n3.ratio低於0.5以下，即使答對了也更要指出不足之處。\n4.綜合之前所有建議,指引下一步方向\n\n###回饋範例###\n作答紀錄1:\n{\"userName\":\"prevention_demo\",\"difficulty\":\"困難\",\"isCorrect\":false,\"userGuess\":0.05,\"truepValue\":0.04105171810328154,\"difference\":0.00994828189671846,\"ratio\":-0.1989656379343692,\"scoreIncrement\":0,\"score\":0,\"life\":2,\"focusMode\":\"預防\",\"feedbackSource\":\"G\"}\n\n反饋內容1:\n【輕易選擇高難度】\n  - 你怎麼敢輕易挑戰困難題目?這完全超出你的實力範圍\n【生命值損失】\n  - 你現在失去一條命了，我建議你要特別小心謹慎,不要再犯錯誤\n【建議】\n  - 從簡單開始，認真對待題目是你的責任！\n\n作答紀錄2:\n{\"userName\":\"prevention_demo\",\"difficulty\":\"普通\",\"isCorrect\":false,\"userGuess\":0.05,\"truepValue\":0.01265759851748487,\"difference\":0.03834240148251512,\"ratio\":-0.7668480296503024,\"scoreIncrement\":0,\"score\":0,\"life\":1,\"focusMode\":\"預防\",\"feedbackSource\":\"G\"}\n\n反饋內容2:\n【未按建議行事】\n  - 儘管我建議你從簡單題目開始練習，但你仍選擇了普通難度，且答案與正確解答相去甚遠...\n【生命值告急】\n  - 你現在僅剩最後一次機會，請三思而後行，避免再次失誤。\n【建議】\n  - 現在唯一的出路就是從最基礎的簡單題目著手，切記不可再貪心挑戰高難度。\n\n作答紀錄3:\n{\"userName\":\"prevention_demo\",\"difficulty\":\"簡單\",\"isCorrect\":true,\"userGuess\":0.05,\"truepValue\":0.7619215887435615,\"difference\":0.7109215887435615,\"ratio\":0.38078411256438527,\"scoreIncrement\":3,\"score\":3,\"life\":1,\"focusMode\":\"預防\",\"feedbackSource\":\"G\"}\n\n反饋內容3:\n【準確性有待加強】\n  - 雖聽取建議選擇簡單難度並取得了正確的結果\n  - 但準確度依然不盡人意。\n【生命值得危險與分數的損失】\n  - 你雖然保護了最後一條生命，但準確度非常低，險些失誤會帶來巨大風險。\n【建議】\n  - 注意每條曲線的平均值（虛線所指位置）和標準差（曲線的寬度）。比較兩者的差異，可以幫助你更準確地描述和理解數據。\n\n在生成反饋時，避免使用積極正面的promotion words,如:\n完成、獲得、成就、成長、進步、希望、渴望、期望、追求、理想、達到、改善、慾望、增加、賺取、動力、擴展、獲取、樂觀的、進展、提升、促進、速度、迅速、朝向、速率、希望\n而是適當使用中性審慎的prevention words,如:\n準確性、逃避、保護、害怕、規避、負責、小心、失敗、風險、焦慮、恐懼、安全、避免、損失、保安、保守、義務、威脅、防禦、應當、警覺、責任、痛苦、逃逸、預防\n\n請盡量精簡並使用繁體中文"
                    }
                ]
            }
        ] 
     # 獲取用戶當前對話歷史
    current_session = prevention_user_history_pValue[user_name]

    # 添加用户的新消息
    current_session.append({
        "role": "user",
        "content": prompt
    })

    response = client.chat.completions.create(
        model = "gpt-4o", #gpt-4o
        temperature = 0.89,
        max_tokens = 500,
        top_p = 1,
        frequency_penalty = 0,
        presence_penalty = 0,
        messages = current_session
    )

    current_session.append({
        "role": "assistant",
        "content": response.choices[0].message.content
     })
    
    # 如對話紀錄超過10條（加上系统消息是11），則剪裁對話歷史，保留系统消息和最近的9條消息
    if len(current_session) > 11:
        # 保留系统消息和最近的9條消息
        prevention_user_history_pValue[user_name] = [current_session[0]] + current_session[-10:]

    return response.choices[0].message.content

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
    print(user_answer)
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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/ttest', methods=['GET', 'POST'])
def handle_tvalue():
    data = request.get_json()
    p_value = data['p_value']
    n = data['n']
    # 自由度
    df = 2 * (n - 1)
    # 計算t值（雙尾，所以p值除以2）
    t_value = t.ppf(1 - p_value / 2, df)
    
    response = jsonify({'t_value': t_value})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True) 