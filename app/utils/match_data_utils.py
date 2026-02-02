import json
import time
from random import choice

from yuyan.app.utils.ad_detect_utils import ad_detect
from yuyan.app.utils.enums import (
    ListMatchRuleEnum,
    ListMatchTypeEnum,
    ListRiskTypeEnum,
    ListStatusEnum,
    ListTypeEnum,
    SwichEnum,
)
from yuyan.app.utils.llm_utils import get_llm_ans
from yuyan.app.utils.tokenizer import AllTokenizer

tokenizer = AllTokenizer()


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        ctx = args[2] if len(args) > 2 else None
        if ctx is not None and hasattr(ctx, "logger"):
            ctx.logger.debug(f"{func.__name__} took {(end_time - start_time)*1000} ms to execute.")
        return result

    return wrapper


@timer
def all_filter(msg, r, ctx, language_pred):
    detail = {
        "contextText": "",
        "filteredText": "",
        "riskType": -1,
        "matchedItem": "",
        "matchedList": "",
        "description": "",
        "descriptionV2": "",
        "matchedDetail": "",
    }

    try:
        cache_game_channel = ctx.config["GAME_CHANNEL"]
        cache_data = ctx.config["CACHE_DATA"]
        chat_sentinel = ctx.config.get("CHAT_SENTINEL", {})

        white_list, ignore_list, black_list = get_white_black_list(msg, cache_game_channel)

        match_words = []
        format_match_words = []

        # 白名单过滤
        return_flag, r = whitelist_filter(
            msg, cache_data, white_list, r, match_words, format_match_words, detail, language_pred
        )
        if return_flag:
            return r

        # 忽略名单
        msg = ignorelist_filter(msg, cache_data, ignore_list, language_pred)

        # 黑名单过滤
        if ac_switch_is_on(ctx, msg):
            blacklist_res = blacklist_filter(
                msg, cache_data, black_list, r, match_words, format_match_words, detail, language_pred, chat_sentinel, True
            )
            return_flag, r = blacklist_res[0], blacklist_res[1]
            if ai_switch_is_on(ctx, msg.gameId):
                return_flag, r = ai_filter(ctx, msg, blacklist_res, r)
        else:
            blacklist_res = blacklist_filter(
                msg, cache_data, black_list, r, match_words, format_match_words, detail, language_pred, chat_sentinel, False
            )
            return_flag, r = blacklist_res[0], blacklist_res[1]
            if ai_switch_is_on(ctx, msg.gameId):
                return_flag, r = ai_filter(ctx, msg, blacklist_res, r)

        if return_flag:
            return r
    except Exception as err:
        ctx.logger.debug(f"自定义规则过滤出错: {err}")
    finally:
        return r


def tokenize_text(text, match_type, text_language=None):
    if ListMatchTypeEnum(int(match_type)) == ListMatchTypeEnum.SEMANTIC:
        text = tokenizer.tokenize(text, drop_prun=True, language=text_language)
    return text


def shumei_swich_is_off(game_channel, ctx, game_id):
    cache_game_channel = ctx.config["GAME_CHANNEL"]
    global_k = "GC_{}_all".format(game_id)
    k = "GC_{}".format(game_channel)
    if cache_game_channel.get(global_k):
        swich_shumei = cache_game_channel[global_k].get("swich_shumei", "")
        if swich_shumei != "":
            swich = int(cache_game_channel[global_k]["swich_shumei"])
            if SwichEnum(swich) == SwichEnum.OFF:
                return True
    if k != global_k and cache_game_channel.get(k):
        swich_shumei = cache_game_channel[k].get("swich_shumei", "")
        if swich_shumei != "":
            swich = int(cache_game_channel[k]["swich_shumei"])
            if SwichEnum(swich) == SwichEnum.OFF:
                return True
    return False


def ai_switch_is_on(ctx, game_id):
    cache_game_channel = ctx.config["GAME_CHANNEL"]
    k = "GC_{}_all".format(game_id)
    if cache_game_channel.get(k, None):
        ai_switch = cache_game_channel[k].get("ai_switch", "")
        if ai_switch != "":
            swich = int(cache_game_channel[k]["ai_switch"])
            if SwichEnum(swich) == SwichEnum.ON:
                return True
    return False


def ac_switch_is_on(ctx, msg):
    cache_game_channel = ctx.config["GAME_CHANNEL"]
    k = f"GC_{msg.channel}"
    global_k = "GC_{}_all".format(msg.gameId)
    if cache_game_channel.get("GC_all_all", None):
        ac_switch = cache_game_channel["GC_all_all"].get("ac_switch", "")
        if ac_switch != "":
            swich = int(cache_game_channel["GC_all_all"]["ac_switch"])
            if SwichEnum(swich) == SwichEnum.ON:
                return True

    if cache_game_channel.get(global_k, None):
        ac_switch = cache_game_channel[global_k].get("ac_switch", "")
        if ac_switch != "":
            swich = int(cache_game_channel[global_k]["ac_switch"])
            if SwichEnum(swich) == SwichEnum.ON:
                return True

    if cache_game_channel.get(k, None):
        ac_switch = cache_game_channel[k].get("ac_switch", "")
        if ac_switch != "":
            swich = int(cache_game_channel[k]["ac_switch"])
            if SwichEnum(swich) == SwichEnum.ON:
                return True
    return False


def whitelist_filter(msg, cache_data, white_list, r, match_words, format_match_words, detail, language_pred):
    for i in white_list:
        if cache_data.get(i):
            name_list = cache_data.get(i)
            if name_list.get("data") and int(name_list.get("status", "")) == ListStatusEnum.ON.value:
                ac_data = name_list["data"]
                match_rule = name_list["match_rule"]
                if match_rule == ListMatchRuleEnum.TEXT_AND_NAME.value:
                    language = [language_pred["text"], language_pred["nickname"]]
                elif match_rule == ListMatchRuleEnum.TEXT.value:
                    language = [language_pred["text"]]
                elif match_rule == ListMatchRuleEnum.ROLE_NAME.value:
                    language = [language_pred["nickname"]]
                else:
                    language = False

                filter_l = ListMatchRuleEnum.enum2filtertext(match_rule, msg)

                for idx, t in enumerate(filter_l):
                    if language and name_list["language"] not in ["", "all"]:
                        if language[idx] != name_list["language"]:
                            continue
                    text = tokenize_text(t, name_list["match_type"])
                    filter_r = ac_data.iter(text)
                    for j in filter_r:
                        match_words.append(str(j[1][1]))
                        format_match_words.append(str(j[1][0]))
                if match_words:
                    detail["contextText"] = ",".join(filter_l)
                    detail["filteredText"] = ",".join(filter_l)
                    detail["riskType"] = ListRiskTypeEnum.NORMAL.value
                    detail["matchedList"] = name_list["name"]
                    detail["matchedItem"] = ",".join(list(set(match_words)))
                    detail["description"] = "白名单"
                    detail["descriptionV2"] = "白名单"

                    r["riskLevel"] = "PASS"
                    r["extra"]["desc"] = "命中自定义白名单"
                    r["extra"]["matchedFmtItem"] = ",".join(list(set(format_match_words)))
                    r["detail"] = detail
                    r["requestId"] = msg.requestId
                    return True, r
    return False, r


def ignorelist_filter(msg, cache_data, ignore_list, language_pred):
    match_words = []
    format_match_words = []
    for i in ignore_list:
        if cache_data.get(i):
            name_list = cache_data.get(i)
            if name_list.get("data") and int(name_list.get("status", "")) == ListStatusEnum.ON.value:
                ac_data = name_list["data"]
                match_rule = int(name_list["match_rule"])
                if match_rule == ListMatchRuleEnum.TEXT_AND_NAME.value:
                    language = [language_pred["text"], language_pred["nickname"]]
                elif match_rule == ListMatchRuleEnum.TEXT.value:
                    language = [language_pred["text"]]
                elif match_rule == ListMatchRuleEnum.ROLE_NAME.value:
                    language = [language_pred["nickname"]]
                else:
                    language = False

                filter_l = ListMatchRuleEnum.enum2filtertext(match_rule, msg)

                for idx, t in enumerate(filter_l):
                    if language and name_list["language"] not in ["", "all"]:
                        if language[idx] != name_list["language"]:
                            continue

                    text = tokenize_text(t, name_list["match_type"])
                    filter_r = ac_data.iter(text)
                    for j in filter_r:
                        match_words.append(str(j[1][1]))
                        format_match_words.append(str(j[1][0]))
                    if match_words:
                        if match_rule == ListMatchRuleEnum.TEXT_AND_NAME.value:
                            if idx == 0:
                                text = msg.text
                                for f in match_words:
                                    text = text.replace(f, "")
                                msg.text = text
                            else:
                                nickname = msg.nickname
                                for f in match_words:
                                    nickname = nickname.replace(f, "")
                                msg.nickname = nickname
                        elif match_rule == ListMatchRuleEnum.TEXT.value:
                            text = msg.text
                            for f in match_words:
                                text = text.replace(f, "")
                            msg.text = text
                        elif match_rule == ListMatchRuleEnum.ROLE_NAME.value:
                            nickname = msg.nickname
                            for f in match_words:
                                nickname = nickname.replace(f, "")
                            msg.nickname = nickname
    return msg


@timer
def blacklist_filter(
    msg, cache_data, black_list, r, match_words, format_match_words, detail, language_pred, chat_sentinel, ac_switch
):
    if chat_sentinel != {}:
        if chat_sentinel["account_id"].get(f"{msg.gameId}_{msg.accountId}", None):
            rule_model = chat_sentinel["account_id"].get(f"{msg.gameId}_{msg.accountId}")[0]
            detail["riskType"] = ListRiskTypeEnum.BLACK_ACCOUNT.value
            detail["matchedList"] = ""
            detail["matchedItem"] = ""
            detail["description"] = "策略模型: {}".format(rule_model)
            detail["descriptionV2"] = "策略模型: {}".format(rule_model)

            r["riskLevel"] = "REJECT"
            r["extra"]["desc"] = "命中自定义策略模型"
            r["detail"] = detail
            r["requestId"] = msg.requestId
            return True, r
        if chat_sentinel["ip"].get(f"{msg.gameId}_{msg.ip}", None):
            rule_model = chat_sentinel["ip"].get(f"{msg.gameId}_{msg.ip}")[0]
            detail["riskType"] = ListRiskTypeEnum.BLACK_IP.value
            detail["matchedList"] = ""
            detail["matchedItem"] = ""
            detail["description"] = "策略模型: {}".format(rule_model)
            detail["descriptionV2"] = "策略模型: {}".format(rule_model)

            r["riskLevel"] = "REJECT"
            r["extra"]["desc"] = "命中自定义策略模型"
            r["detail"] = detail
            r["requestId"] = msg.requestId
            return True, r

    if not ac_switch:
        return False, r

    match_name_list = []
    risk_types = []
    match_rule_list = []
    all_word_positions = []
    matched_detail = []
    for b in black_list:
        match_detail_item = {
            "listId": "",
            "matchedFiled": [],
            "name": "",
            "organization": "",
            "wordPositions": [],
            "words": [],
        }

        if cache_data.get(b):
            name_list = cache_data.get(b)
            if name_list.get("data") and int(name_list.get("status", "")) == ListStatusEnum.ON.value:
                ac_data = name_list["data"]
                match_rule = int(name_list["match_rule"])
                if match_rule == ListMatchRuleEnum.TEXT_AND_NAME.value:
                    language = [language_pred["text"], language_pred["nickname"]]
                elif match_rule == ListMatchRuleEnum.TEXT.value:
                    language = [language_pred["text"]]
                elif match_rule == ListMatchRuleEnum.ROLE_NAME.value:
                    language = [language_pred["nickname"]]
                else:
                    language = False

                filter_l = ListMatchRuleEnum.enum2filtertext(match_rule, msg)
                for idx, t in enumerate(filter_l):
                    if language and name_list["language"] not in ["", "all"]:
                        text_language = language[idx]
                        if text_language != name_list["language"]:
                            continue
                    else:
                        text_language = language[idx] if language else None

                    single_match_word = []
                    single_position = []
                    single_format_match_word = []

                    text = tokenize_text(t, name_list["match_type"], text_language)

                    filter_r = ac_data.iter(text)
                    for i in filter_r:
                        raw_word = str(i[1][1])
                        filter_word = str(i[1][0])
                        single_match_word.append(raw_word)
                        single_format_match_word.append(filter_word)
                        single_position.append(list(range(t.find(raw_word), t.find(raw_word) + len(raw_word))))
                    if single_match_word:
                        match_rule_list.append(t)
                        match_words.extend(single_match_word)
                        format_match_words.extend(single_format_match_word)
                        match_name_list.append(name_list["name"])
                        risk_types.append(name_list["risk_type"])

                        match_detail_item["listId"] = b
                        match_detail_item["matchedFiled"] = ListMatchRuleEnum.desc(match_rule)
                        match_detail_item["name"] = name_list["name"]
                        match_detail_item["words"] = single_match_word
                        for p, w in zip(single_position, single_match_word):
                            match_detail_item["wordPositions"].append(
                                {"position": ",".join("%s" % i for i in p), "word": w}
                            )
                            all_word_positions.extend(p)

                        matched_detail.append(match_detail_item)

    if match_words:
        match_rule_list = list(set(match_rule_list))
        if msg.text not in match_rule_list:
            detail["contextText"] = match_rule_list[0]
            risk_type = choice(risk_types)
            if msg.ip in match_rule_list or msg.accountId in match_rule_list:
                detail["riskType"] = int(risk_type)
            else:
                detail["riskType"] = ListRiskTypeEnum.NICKNAME_RISK.value
        else:
            if len(match_rule_list) == 1:
                detail["contextText"] = match_rule_list[0] if match_rule_list else ""
                sent_cp = detail["contextText"]
                for i in match_words:
                    sent_cp = sent_cp.lower().replace(i.lower(), "*" * len(i))
                detail["filteredText"] = sent_cp
                risk_type = choice(risk_types)
                detail["riskType"] = int(risk_type)
            else:
                detail["contextText"] = match_rule_list[0] if match_rule_list else ""
                detail["riskType"] = ListRiskTypeEnum.NICKNAME_RISK.value

        detail["matchedList"] = ",".join(list(set(match_name_list)))
        detail["matchedItem"] = ",".join(list(set(match_words)))
        detail["description"] = "黑名单: {}".format(ListRiskTypeEnum.desc(int(risk_type)))
        detail["descriptionV2"] = "黑名单: {}".format(ListRiskTypeEnum.desc(int(risk_type)))
        detail["matchedDetail"] = json.dumps(matched_detail, ensure_ascii=False)

        all_word_positions = list(set(all_word_positions))
        all_word_positions.sort()
        detail["hitPosition"] = ",".join("%s" % i for i in all_word_positions) if all_word_positions else ""

        r["riskLevel"] = "REJECT"
        r["extra"]["desc"] = "命中自定义黑名单"
        r["extra"]["matchedFmtItem"] = ",".join(list(set(format_match_words)))
        r["detail"] = detail
        r["requestId"] = msg.requestId
        return True, r

    r["detail"] = detail
    r["requestId"] = msg.requestId
    return False, r


def get_white_black_list(msg, cache_game_channel):
    white_list = []
    ignore_list = []
    black_list = []
    if cache_game_channel.get("GC_{}".format(msg.channel)):
        gc = cache_game_channel.get("GC_{}".format(msg.channel))
        if gc.get(str(ListTypeEnum.WHITELIST.value)):
            white_list.extend(gc.get(str(ListTypeEnum.WHITELIST.value)))
        if gc.get(str(ListTypeEnum.IGNORE.value)):
            ignore_list.extend(gc.get(str(ListTypeEnum.IGNORE.value)))
        if gc.get(str(ListTypeEnum.SENSITIVE.value)):
            black_list.extend(gc.get(str(ListTypeEnum.SENSITIVE.value)))

    if cache_game_channel.get("GC_{}_all".format(str(msg.gameId))):
        gc = cache_game_channel.get("GC_{}_all".format(str(msg.gameId)))
        if gc.get(str(ListTypeEnum.WHITELIST.value)):
            white_list.extend(gc.get(str(ListTypeEnum.WHITELIST.value)))
        if gc.get(str(ListTypeEnum.IGNORE.value)):
            ignore_list.extend(gc.get(str(ListTypeEnum.IGNORE.value)))
        if gc.get(str(ListTypeEnum.SENSITIVE.value)):
            black_list.extend(gc.get(str(ListTypeEnum.SENSITIVE.value)))

    if cache_game_channel.get("GC_all_all"):
        gc = cache_game_channel.get("GC_all_all")
        if gc.get(str(ListTypeEnum.WHITELIST.value)):
            white_list.extend(gc.get(str(ListTypeEnum.WHITELIST.value)))
        if gc.get(str(ListTypeEnum.IGNORE.value)):
            ignore_list.extend(gc.get(str(ListTypeEnum.IGNORE.value)))
        if gc.get(str(ListTypeEnum.SENSITIVE.value)):
            black_list.extend(gc.get(str(ListTypeEnum.SENSITIVE.value)))
    return white_list, ignore_list, black_list


def ai_filter(ctx, msg, blacklist_res, r):
    ad_res = ad_detect(msg, ctx)
    ctx.logger.debug(f"广告模型返回: {ad_res}")
    ad_result = ad_res["data"][0].get("label", None) if ad_res else None

    blacklist_flag = blacklist_res[0]
    detail = blacklist_res[1]["detail"] if blacklist_res[1].get("detail", "") else {}

    if blacklist_flag:
        if ad_result == "REJECT":
            detail["riskType"] = 310
            detail["description"] = "广告拉人"
            detail["descriptionV2"] = "广告拉人"
            detail["filteredText"] = ""
            r["detail"] = detail
            r["riskLevel"] = "REJECT"
            return True, r
        llm_ans = get_llm_ans(msg.gameId, msg.text, msg.chat_history)
        if llm_ans:
            detail["riskType"] = 310
            detail["description"] = "广告拉人:卖号"
            detail["descriptionV2"] = "广告拉人:卖号"
            detail["filteredText"] = ""
            r["detail"] = detail
            r["riskLevel"] = "REJECT"
            return True, r
        return True, blacklist_res[1]

    if ad_result == "REJECT":
        detail["riskType"] = 310
        detail["description"] = "广告拉人"
        detail["descriptionV2"] = "广告拉人"
        r["detail"] = detail
        r["riskLevel"] = "REJECT"
        return True, r

    llm_ans = get_llm_ans(msg.gameId, msg.text, msg.chat_history)
    if llm_ans:
        detail["riskType"] = 310
        detail["description"] = "广告拉人:卖号"
        detail["descriptionV2"] = "广告拉人:卖号"
        detail["filteredText"] = ""
        r["detail"] = detail
        r["riskLevel"] = "REJECT"
        return True, r
    return False, r
