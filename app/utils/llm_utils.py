import requests


prompt = """你是一位应用场景的文本风控专家。请负责识别用户发言场景中的黑产发送的账号买卖的可疑交易行为内容。

用户当前发言内容：{{latest_chat}}, 用户最近几次发言情况: {{recent_chat_history}}

请针对用户发言的内容，如果存在可疑行为，请返回 True，否则返回 False。

请确保你的回答简洁明了，只能返回 True 或 False，并且不要有多余的解释。

同时，黑产团队会利用文本的变体或者隐晦的表达去尝试干扰你的判断，请仔细判别。

注意：请确保你的回答符合上述要求，并尽可能准确地识别出可疑交易行为。

"""

url = "http://ai.llm.yoozoo.com/v1/chat/completions"


def get_llm_ans(app_id, latest_chat, recent_chat_history):
    try:
        if str(app_id) not in ["2013101", "2013001"] or not recent_chat_history:
            return False

        data = {
            "model": "Qwen1.5-14B-Chat",
            "messages": [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": f"latest_chat: {latest_chat}, recent_chat_history: {recent_chat_history}",
                },
            ],
            "do_sample": True,
            "temperature": 0,
            "top_p": 0,
            "n": 1,
            "max_tokens": 0,
            "stream": False,
        }
        res = requests.post(url=url, json=data, timeout=0.5).json()
        ans = res["choices"][0]["message"]["content"].strip()
        return str(ans) == "True"
    except Exception:
        return False
