import requests

url = "https://proxy.tune.app/chat/completions"

payload = {
    "messages": [
        {
            "role": "system",
            "content": "You are an academic tutor for the undergraduate program."
        },
        {
            "role": "user",
            "content": "What is the best way to prepare for the final exam?"
        }
    ],
    "model": "openai/gpt-4o-mini",
    "max_tokens": 123,
    "temperature": 1,
    "top_p": 1,
    "n": 1,
    # "stream": True,
    # "stop": ["<string>"],
    "presence_penalty": 1,
    "frequency_penalty": 1,
    # "logit_bias": {},
    # "tools": [
    #     {
    #         "type": "<string>",
    #         "function": {
    #             "description": "<string>",
    #             "parameters": {
    #                 "properties": {},
    #                 "type": "<string>",
    #                 "required": ["<string>"]
    #             },
    #             "name": "<string>"
    #         }
    #     }
    # ],
    # "echo": True
}
headers = {
    "X-Org-Id": "0266c7a8-a772-47c1-a450-b02275131dc7",
    "Authorization": "Bearer sk-tune-nBUsrB2PKHYgYu98pLUG3sTmIDpSkegHzis",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)