import time


def ad_detect(msg, ctx):
    t1 = time.time()
    if msg.text == "" or "NICKNAME_CHECK" in msg.channel:
        ctx.logger.debug(f"ad detect api costs: {(time.time() - t1) * 1000} ms")
        return False
    url = ctx.config.get("AD_DETECT_URL", "")
    if not url:
        return False
    headers = {"Content-Type": "application/json"}
    params = {
        "nickname": msg.nickname,
        "text": msg.text,
        "score_threshold": get_threshold(ctx, msg.app_id),
    }
    res = False
    try:
        session = ctx.config.get("REQUESTS_SESSION")
        response = session.post(url=url, headers=headers, json=params, timeout=(0.8, 0.8)).json()
        if response.get("code") == 0:
            res = response
    except Exception as err:
        ctx.logger.debug(f"ad detect api err: {err}")
    finally:
        ctx.logger.debug(f"ad detect api costs: {(time.time() - t1) * 1000} ms")
        return res


def get_threshold(ctx, app_id):
    cache_app_channel = ctx.config.get("APP_CHANNEL", {})
    k = "AC_{}_all".format(app_id)
    if cache_app_channel.get(k):
        threshold = cache_app_channel[k].get("model_threshold", "")
        if threshold != "":
            return cache_app_channel[k]["model_threshold"]
    return 0.8
