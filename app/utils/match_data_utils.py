import json
import time
from random import choice

from app.utils.ad_detect_utils import ad_detect
from app.utils.enums import (
    ListMatchRuleEnum,
    ListMatchTypeEnum,
    ListRiskTypeEnum,
    ListLanguageScopeEnum,
    ListStatusEnum,
    ListTypeEnum,
    SwichEnum,
)
from app.utils.llm_utils import get_llm_ans
from app.utils.tokenizer import AllTokenizer

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
        cache_app_channel = ctx.config["APP_CHANNEL"]
        cache_data = ctx.config["CACHE_DATA"]
        chat_sentinel = ctx.config.get("CHAT_SENTINEL", {})

        white_list, ignore_list, black_list = get_white_black_list(msg, cache_app_channel)

        # 白名单过滤
        return_flag, r = whitelist_filter(
            msg, cache_data, white_list, r, detail, language_pred
        )
        if return_flag:
            return r

        # 忽略名单
        msg = ignorelist_filter(msg, cache_data, ignore_list, language_pred)

        # 黑名单过滤
        if ac_switch_is_on(ctx, msg):
            blacklist_res = blacklist_filter(
                msg, cache_data, black_list, r, detail, language_pred, chat_sentinel, True
            )
            return_flag, r = blacklist_res[0], blacklist_res[1]
            if ai_switch_is_on(ctx, msg.app_id):
                return_flag, r = ai_filter(ctx, msg, blacklist_res, r)
        else:
            blacklist_res = blacklist_filter(
                msg, cache_data, black_list, r, detail, language_pred, chat_sentinel, False
            )
            return_flag, r = blacklist_res[0], blacklist_res[1]
            if ai_switch_is_on(ctx, msg.app_id):
                return_flag, r = ai_filter(ctx, msg, blacklist_res, r)

        if return_flag:
            return r
    except Exception as err:
        ctx.logger.debug(f"自定义规则过滤出错: {err}")
    return r


def tokenize_text(text, match_type, text_language=None):
    if ListMatchTypeEnum(int(match_type)) == ListMatchTypeEnum.SEMANTIC:
        text = tokenizer.tokenize(text, drop_prun=True, language=text_language)
    return text


def _dedup(items):
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _is_list_active(name_list):
    return name_list.get("data") and int(name_list.get("status", "")) == ListStatusEnum.ON.value


def _get_match_languages(match_rule, language_pred):
    if match_rule == ListMatchRuleEnum.TEXT_AND_NAME.value:
        return [language_pred["text"], language_pred["nickname"]]
    if match_rule == ListMatchRuleEnum.TEXT.value:
        return [language_pred["text"]]
    if match_rule == ListMatchRuleEnum.ROLE_NAME.value:
        return [language_pred["nickname"]]
    return None


def _iter_ac_matches(ac_data, text, match_type, text_language):
    tokenized = tokenize_text(text, match_type, text_language)
    for item in ac_data.iter(tokenized):
        raw_word = str(item[1][1])
        filter_word = str(item[1][0])
        yield raw_word, filter_word


def _collect_match_words(name_list, msg, language_pred):
    match_rule = int(name_list["match_rule"])
    languages = _get_match_languages(match_rule, language_pred)
    filter_texts = ListMatchRuleEnum.enum2filtertext(match_rule, msg)
    results = []
    for idx, text in enumerate(filter_texts):
        text_language = languages[idx] if languages else None
        if languages and not _language_allowed(name_list, text_language):
            results.append((text, text_language, [], []))
            continue
        raw_words = []
        format_words = []
        for raw_word, filter_word in _iter_ac_matches(
            name_list["data"], text, name_list["match_type"], text_language
        ):
            raw_words.append(raw_word)
            format_words.append(filter_word)
        results.append((text, text_language, raw_words, format_words))
    return match_rule, filter_texts, results


def _apply_remove(text, words):
    for w in words:
        text = text.replace(w, "")
    return text


def _apply_sentinel_hit(detail, r, risk_type, rule_model):
    detail["riskType"] = risk_type
    detail["matchedList"] = ""
    detail["matchedItem"] = ""
    detail["description"] = "策略模型: {}".format(rule_model)
    detail["descriptionV2"] = "策略模型: {}".format(rule_model)
    r["riskLevel"] = "REJECT"
    r["extra"]["desc"] = "命中自定义策略模型"
    r["detail"] = detail
    r["requestId"] = r.get("requestId") or ""
    return True, r


def _check_chat_sentinel(chat_sentinel, msg, detail, r):
    if not chat_sentinel:
        return False, r
    account_hit = chat_sentinel["account_id"].get(f"{msg.app_id}_{msg.account_id}", None)
    if account_hit:
        return _apply_sentinel_hit(detail, r, ListRiskTypeEnum.BLACK_ACCOUNT.value, account_hit[0])
    ip_hit = chat_sentinel["ip"].get(f"{msg.app_id}_{msg.ip}", None)
    if ip_hit:
        return _apply_sentinel_hit(detail, r, ListRiskTypeEnum.BLACK_IP.value, ip_hit[0])
    return False, r


def _build_matched_detail_item(list_id, match_rule, name, words, positions):
    item = {
        "listId": list_id,
        "matchedFiled": ListMatchRuleEnum.desc(match_rule),
        "name": name,
        "organization": "",
        "wordPositions": [],
        "words": words,
    }
    for p, w in zip(positions, words):
        item["wordPositions"].append({"position": ",".join("%s" % i for i in p), "word": w})
    return item


def _collect_blacklist_hits(black_list, cache_data, msg, language_pred):
    aggregate = {
        "match_words": [],
        "format_match_words": [],
        "match_name_list": [],
        "risk_types": [],
        "match_rule_list": [],
        "all_word_positions": [],
        "matched_detail": [],
    }
    for list_no in black_list:
        name_list = cache_data.get(list_no)
        if not name_list or not _is_list_active(name_list):
            continue
        match_rule = int(name_list["match_rule"])
        languages = _get_match_languages(match_rule, language_pred)
        filter_l = ListMatchRuleEnum.enum2filtertext(match_rule, msg)
        for idx, text in enumerate(filter_l):
            text_language = languages[idx] if languages else None
            if languages and not _language_allowed(name_list, text_language):
                continue
            single_match_words = []
            single_positions = []
            single_format_words = []
            for raw_word, filter_word in _iter_ac_matches(
                name_list["data"], text, name_list["match_type"], text_language
            ):
                single_match_words.append(raw_word)
                single_format_words.append(filter_word)
                single_positions.append(list(range(text.find(raw_word), text.find(raw_word) + len(raw_word))))
            if not single_match_words:
                continue
            aggregate["match_rule_list"].append(text)
            aggregate["match_words"].extend(single_match_words)
            aggregate["format_match_words"].extend(single_format_words)
            aggregate["match_name_list"].append(name_list["name"])
            aggregate["risk_types"].append(name_list["risk_type"])
            aggregate["matched_detail"].append(
                _build_matched_detail_item(
                    list_no, match_rule, name_list["name"], single_match_words, single_positions
                )
            )
            for p in single_positions:
                aggregate["all_word_positions"].extend(p)
    return aggregate


def _build_blacklist_detail(aggregate, msg, detail):
    match_words = aggregate["match_words"]
    if not match_words:
        return False

    match_rule_list = list(set(aggregate["match_rule_list"]))
    risk_type = choice(aggregate["risk_types"]) if aggregate["risk_types"] else ListRiskTypeEnum.NICKNAME_RISK.value

    if msg.text not in match_rule_list:
        detail["contextText"] = match_rule_list[0] if match_rule_list else ""
        if msg.ip in match_rule_list or msg.account_id in match_rule_list:
            detail["riskType"] = int(risk_type)
        else:
            detail["riskType"] = ListRiskTypeEnum.NICKNAME_RISK.value
    else:
        if len(match_rule_list) == 1:
            detail["contextText"] = match_rule_list[0] if match_rule_list else ""
            sent_cp = detail["contextText"]
            for word in match_words:
                sent_cp = sent_cp.lower().replace(word.lower(), "*" * len(word))
            detail["filteredText"] = sent_cp
            detail["riskType"] = int(risk_type)
        else:
            detail["contextText"] = match_rule_list[0] if match_rule_list else ""
            detail["riskType"] = ListRiskTypeEnum.NICKNAME_RISK.value

    detail["matchedList"] = ",".join(list(set(aggregate["match_name_list"])))
    detail["matchedItem"] = ",".join(list(set(match_words)))
    detail["description"] = "黑名单: {}".format(ListRiskTypeEnum.desc(int(risk_type)))
    detail["descriptionV2"] = "黑名单: {}".format(ListRiskTypeEnum.desc(int(risk_type)))
    detail["matchedDetail"] = json.dumps(aggregate["matched_detail"], ensure_ascii=False)

    all_word_positions = list(set(aggregate["all_word_positions"]))
    all_word_positions.sort()
    detail["hitPosition"] = ",".join("%s" % i for i in all_word_positions) if all_word_positions else ""
    return True


def _parse_language_codes(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(i).strip().lower() for i in raw if str(i).strip()]
    if isinstance(raw, str):
        raw_str = raw.strip()
        if not raw_str:
            return []
        if raw_str.startswith("["):
            try:
                parsed = json.loads(raw_str)
                if isinstance(parsed, list):
                    return [str(i).strip().lower() for i in parsed if str(i).strip()]
            except Exception:
                pass
        return [str(i).strip().lower() for i in raw_str.split(",") if str(i).strip()]
    return []


def _get_language_scope_and_codes(name_list):
    scope_raw = name_list.get("language_scope")
    scope = str(scope_raw).strip().upper() if scope_raw else ""
    codes = _parse_language_codes(name_list.get("language_codes"))
    if not scope:
        legacy = str(name_list.get("language") or "").strip().lower()
        if legacy and legacy != "all":
            return ListLanguageScopeEnum.SPECIFIC.value, [legacy]
        return ListLanguageScopeEnum.ALL.value, []
    if scope == ListLanguageScopeEnum.SPECIFIC.value:
        if not codes:
            legacy = str(name_list.get("language") or "").strip().lower()
            if legacy and legacy != "all":
                codes = [legacy]
        return scope, codes
    if scope == ListLanguageScopeEnum.ALL.value:
        return scope, []
    return ListLanguageScopeEnum.ALL.value, []


def _language_allowed(name_list, language_value):
    scope, codes = _get_language_scope_and_codes(name_list)
    if not language_value:
        return scope == ListLanguageScopeEnum.ALL.value
    lang = str(language_value).strip().lower()
    if not lang:
        return scope == ListLanguageScopeEnum.ALL.value
    if scope == ListLanguageScopeEnum.ALL.value:
        return True
    if scope == ListLanguageScopeEnum.SPECIFIC.value and not codes:
        return False
    return lang in codes


def shumei_swich_is_off(app_channel, ctx, app_id):
    cache_app_channel = ctx.config["APP_CHANNEL"]
    global_k = "AC_{}_all".format(app_id)
    k = "AC_{}".format(app_channel)
    if cache_app_channel.get(global_k):
        swich_shumei = cache_app_channel[global_k].get("swich_shumei", "")
        if swich_shumei != "":
            swich = int(cache_app_channel[global_k]["swich_shumei"])
            if SwichEnum(swich) == SwichEnum.OFF:
                return True
    if k != global_k and cache_app_channel.get(k):
        swich_shumei = cache_app_channel[k].get("swich_shumei", "")
        if swich_shumei != "":
            swich = int(cache_app_channel[k]["swich_shumei"])
            if SwichEnum(swich) == SwichEnum.OFF:
                return True
    return False


def ai_switch_is_on(ctx, app_id):
    cache_app_channel = ctx.config["APP_CHANNEL"]
    k = "AC_{}_all".format(app_id)
    if cache_app_channel.get(k, None):
        ai_switch = cache_app_channel[k].get("ai_switch", "")
        if ai_switch != "":
            swich = int(cache_app_channel[k]["ai_switch"])
            if SwichEnum(swich) == SwichEnum.ON:
                return True
    return False


def ac_switch_is_on(ctx, msg):
    cache_app_channel = ctx.config["APP_CHANNEL"]
    k = f"AC_{msg.channel}"
    global_k = "AC_{}_all".format(msg.app_id)
    keys = ["AC_all_all", global_k, k]
    values = []
    for key in keys:
        if cache_app_channel.get(key, None):
            ac_switch = cache_app_channel[key].get("ac_switch", "")
            if ac_switch != "":
                values.append(ac_switch)
    if not values:
        # 没有配置开关时，默认放行匹配规则
        return True
    for value in values:
        try:
            if SwichEnum(int(value)) == SwichEnum.ON:
                return True
        except Exception:
            continue
    return False


def whitelist_filter(msg, cache_data, white_list, r, detail, language_pred):
    for i in white_list:
        if cache_data.get(i):
            name_list = cache_data.get(i)
            if _is_list_active(name_list):
                _, filter_l, results = _collect_match_words(name_list, msg, language_pred)
                match_words = []
                format_match_words = []
                for _, _, raw_words, fmt_words in results:
                    match_words.extend(raw_words)
                    format_match_words.extend(fmt_words)
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
                    return True, r
    return False, r


def ignorelist_filter(msg, cache_data, ignore_list, language_pred):
    for i in ignore_list:
        if cache_data.get(i):
            name_list = cache_data.get(i)
            if _is_list_active(name_list):
                match_rule, _, results = _collect_match_words(name_list, msg, language_pred)
                for idx, (_, _, raw_words, _) in enumerate(results):
                    if not raw_words:
                        continue
                    if match_rule == ListMatchRuleEnum.TEXT_AND_NAME.value:
                        if idx == 0:
                            text = msg.text
                            for f in raw_words:
                                text = text.replace(f, "")
                            msg.text = text
                        else:
                            nickname = msg.nickname
                            for f in raw_words:
                                nickname = nickname.replace(f, "")
                            msg.nickname = nickname
                    elif match_rule == ListMatchRuleEnum.TEXT.value:
                        text = msg.text
                        for f in raw_words:
                            text = text.replace(f, "")
                        msg.text = text
                    elif match_rule == ListMatchRuleEnum.ROLE_NAME.value:
                        nickname = msg.nickname
                        for f in raw_words:
                            nickname = nickname.replace(f, "")
                        msg.nickname = nickname
    return msg


@timer
def blacklist_filter(
    msg, cache_data, black_list, r, detail, language_pred, chat_sentinel, ac_switch
):
    sentinel_hit, r = _check_chat_sentinel(chat_sentinel, msg, detail, r)
    if sentinel_hit:
                    return True, r

    if not ac_switch:
        return False, r
    aggregate = _collect_blacklist_hits(black_list, cache_data, msg, language_pred)
    if _build_blacklist_detail(aggregate, msg, detail):
        r["riskLevel"] = "REJECT"
        r["extra"]["desc"] = "命中自定义黑名单"
        r["extra"]["matchedFmtItem"] = ",".join(list(set(aggregate["format_match_words"])))
        r["detail"] = detail
        r["requestId"] = msg.request_id
        return True, r

    r["detail"] = detail
    r["requestId"] = msg.request_id
    return False, r


def get_white_black_list(msg, cache_app_channel):
    white_list = []
    ignore_list = []
    black_list = []
    if cache_app_channel.get("AC_{}".format(msg.channel)):
        gc = cache_app_channel.get("AC_{}".format(msg.channel))
        if gc.get(str(ListTypeEnum.WHITELIST.value)):
            white_list.extend(gc.get(str(ListTypeEnum.WHITELIST.value)))
        if gc.get(str(ListTypeEnum.IGNORE.value)):
            ignore_list.extend(gc.get(str(ListTypeEnum.IGNORE.value)))
        if gc.get(str(ListTypeEnum.SENSITIVE.value)):
            black_list.extend(gc.get(str(ListTypeEnum.SENSITIVE.value)))

    if cache_app_channel.get("AC_{}_all".format(str(msg.app_id))):
        gc = cache_app_channel.get("AC_{}_all".format(str(msg.app_id)))
        if gc.get(str(ListTypeEnum.WHITELIST.value)):
            white_list.extend(gc.get(str(ListTypeEnum.WHITELIST.value)))
        if gc.get(str(ListTypeEnum.IGNORE.value)):
            ignore_list.extend(gc.get(str(ListTypeEnum.IGNORE.value)))
        if gc.get(str(ListTypeEnum.SENSITIVE.value)):
            black_list.extend(gc.get(str(ListTypeEnum.SENSITIVE.value)))

    if cache_app_channel.get("AC_all_all"):
        gc = cache_app_channel.get("AC_all_all")
        if gc.get(str(ListTypeEnum.WHITELIST.value)):
            white_list.extend(gc.get(str(ListTypeEnum.WHITELIST.value)))
        if gc.get(str(ListTypeEnum.IGNORE.value)):
            ignore_list.extend(gc.get(str(ListTypeEnum.IGNORE.value)))
        if gc.get(str(ListTypeEnum.SENSITIVE.value)):
            black_list.extend(gc.get(str(ListTypeEnum.SENSITIVE.value)))
    return _dedup(white_list), _dedup(ignore_list), _dedup(black_list)


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
        llm_ans = get_llm_ans(msg.app_id, msg.text, msg.chat_history)
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

    llm_ans = get_llm_ans(msg.app_id, msg.text, msg.chat_history)
    if llm_ans:
        detail["riskType"] = 310
        detail["description"] = "广告拉人:卖号"
        detail["descriptionV2"] = "广告拉人:卖号"
        detail["filteredText"] = ""
        r["detail"] = detail
        r["riskLevel"] = "REJECT"
        return True, r
    return False, r
