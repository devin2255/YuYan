import json


class LanguageClassification(object):
    @classmethod
    def predict(cls, msg, ctx):
        url = ctx.config.get("LANGUAGE_CLS_URL", "")
        if not url:
            return False
        headers = {"Content-Type": "application/json"}
        params = {"nickname": msg.nickname, "text": msg.text}
        try:
            session = ctx.config.get("REQUESTS_SESSION")
            response = session.post(url=url, headers=headers, json=params, timeout=0.2).text
            return json.loads(response)
        except Exception as err:
            ctx.logger.debug(f"language predict err: {err}")
            return False
