import requests
import json

class ChatGPT():
    def __init__(self, model_path = 'gpt-3.5-turbo', api_key = None):
        self.model_path = model_path
        self.api_key = api_key

    def chat(self, message):
        payload = json.dumps({
            "model": self.model_path,
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "safe_mode": False
        })
        url = "https://oa.api2d.net/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return json.loads(str(response.text))['choices'][0]['message']['content']

if __name__ == '__main__':
    model = ChatGPT(api_key='fk**')
    print(model.chat('讲个笑话'))