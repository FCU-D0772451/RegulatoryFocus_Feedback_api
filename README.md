# 相關係數猜測遊戲之回饋系統後端

這是一個基於 Flask 和 OpenAI API 的互動式統計學習系統，提供「相關係數猜測」和「p-value 顯著性判斷」兩種遊戲模式的回饋生成，並根據用戶的調節焦點（促進/預防）提供個性化回饋。

## 專案架構
```
correlation_game/
├── app.py                 # Flask 主應用程式
├── chat_handlers.py       # OpenAI 對話處理邏輯
├── stats_handlers.py      # 統計計算功能
├── globals.py            # 全局變數管理
├── requirements.txt      # 依賴套件列表
├── vercel.json           # vercel部屬
└── README.md             # 本文件
```

## 技術細節
### 核心技術
- 後端框架: Flask
- AI 服務: OpenAI GPT-4o
- 統計計算: SciPy
- 跨域支持: Flask-CORS
- 部屬: Vercel

### 特色功能
- 雙模式調節焦點回饋
  - 促進焦點: 強調成長、進步的積極回饋
  - 預防焦點: 注重準確性、風險防範的謹慎回饋
- 三級難度系統
  - 簡單/普通/困難對應不同的容錯閾值
  - 動態計分機制 (score = 基礎分 × ratio)
- 對話歷史記憶
  - 自動維護最近 10 輪對話上下文
  - 用戶專屬對話記憶

## API 文檔
### 基礎 URL
http://your-domain.com 或 http://localhost:5000

### 1. 相關係數猜測遊戲
Endpoint: POST /chat_correlation

**請求格式:**
```json
{
  "prompt": "{\"userName\":\"玩家名稱\",\"difficulty\":\"困難\",\"focusMode\":\"促進\",...}"
}
```
**必要字段:**
- userName: 唯一用戶識別
- difficulty: 難度級別 (簡單/普通/困難)
- focusMode: 回饋模式 (促進/預防)
- userGuess: 用戶猜測值 (0~1)
- trueCorrelation: 實際相關係數
- life: 剩餘生命值

**成功回應:**
```json
{
  "response": "【卓越表現】\n- 您的猜測非常接近真實值..."
}
```

### 2. p-value 顯著性判斷
Endpoint: POST /chat_pValue

**請求格式:**
```json
{
  "prompt": "{\"userName\":\"玩家名稱\",\"difficulty\":\"普通\",...}"
}
```
**特殊字段:**
- userGuess: 用戶猜測的 p-value
- truepValue: 實際 p-value

### 3. t檢定計算工具  
Endpoint: POST /ttest

**請求格式:**
```json
{
  "p_value": 0.05,
  "n": 30
}
```
**成功回應:**
```json
{
  "t_value": 2.045
}
```

## 本地開發指南
### 環境設置
1. 安裝依賴:
```bash
pip install -r requirements.txt
```
2. 設置環境變數:
```bash
export OPENAI_API_KEY='your-api-key'
```
3. 啟動服務:
```bash  
python app.py
```

### 測試範例
```python
import requests

url = "http://localhost:5000/chat_correlation"
data = {
    "prompt": json.dumps({
        "userName": "test_user",
        "difficulty": "簡單",
        "focusMode": "促進",
        "userGuess": 0.8,
        "trueCorrelation": 0.75,
        "difference": 0.05,
        "life": 3
    })
}

response = requests.post(url, json=data)
print(response.json())
```

## 部署建議
### 生產環境部署:
```bash
gunicorn -w 4 -b :5000 app:app
```
### 環境變數管理:
- 通過 .env 文件管理敏感信息
- 使用 python-dotenv 加載配置
### 持久化方案:
- 建議將對話歷史存入 Redis 或 PostgreSQL
- 定期備份用戶進度