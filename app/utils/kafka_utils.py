import collections
import json


def submit_kafka(data_params, response, ctx):
    try:
        one_row = write_hdfs_log(data_params, response)
        tag = "plat_" + str(data_params["gameId"]) + "_chatmsg"
        log_line = str(tag) + "\t" + str(one_row)
        ctx.kafka_logger.write_msg(log_line)

        qp_dict = {"request_data": data_params, "response_data": response, "game_id": str(data_params["gameId"])}
        ctx.kafka_logger.write_query(json.dumps(qp_dict, ensure_ascii=False))

        text_dict = transfor_json(data_params, response)
        ctx.kafka_logger.write_json(json.dumps(text_dict, ensure_ascii=False))
    except Exception as err:
        ctx.logger.debug(f"write request log err: {err}")


def submit_img_kafka(data_params, response, ctx):
    try:
        qp_dict = {"request_data": data_params, "response_data": response, "game_id": str(data_params["gameId"])}
        ctx.kafka_logger.write_query(json.dumps(qp_dict, ensure_ascii=False))
        img_dict = {}
        img_dict.update(data_params)
        img_dict.update(response)
        img_dict["game_id"] = str(data_params["gameId"])
        ctx.kafka_logger.write_img(json.dumps(img_dict, ensure_ascii=False))
    except Exception as err:
        ctx.logger.debug(f"write img request log err: {err}")


def write_hdfs_log(data_json, response):
    data_json = collections.defaultdict(handle, data_json)
    response = collections.defaultdict(handle, response)
    one_row = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
        str(data_json["btId"]),
        str(data_json["timestamp"]),
        str(data_json["tokenId"]),
        str(data_json["nickname"]).replace("'", "").replace("|", "").replace("\n", ""),
        str(data_json["text"]).replace("\r", "").replace("'", "").replace("|", "").replace("\n", ""),
        str(data_json["gameId"]),
        str(data_json["serverId"]),
        str(data_json["accountId"]),
        str(data_json["roleId"]),
        str(data_json["vipLevel"]),
        str(data_json["level"]),
        str(data_json["ip"]),
        str(data_json["channel"]),
        str(data_json["relationship"]),
        str(data_json["targetId"]),
        str(data_json["organizationId"]),
        str(data_json["teamId"]),
        str(data_json["sceneId"]),
        str(data_json["mac"]),
        str(data_json["uuid"]),
        str(data_json["idfv"]),
        str(data_json["idfa"]),
        str(data_json["deviceId"]),
        str(data_json["phone"]),
        str(data_json["imei"]),
        str(data_json["title"]).replace("|", ""),
        str(data_json["topic"]).replace("|", ""),
        str(data_json["nickocr"]).replace("|", ""),
        str(data_json["channelId"]),
        str(data_json["sumPay"]),
        str(data_json["logtime"]),
        str(data_json["logday"]),
        str(data_json["lastPay"]),
        str(data_json["lastPayDay"]),
        str(data_json["lastLogin"]),
        str(data_json["lastLoginDay"]),
        str(data_json["lastLogout"]),
        str(data_json["lastLogoutDay"]),
        str(data_json["deviceType"]),
        str(response["code"]),
        str(json.dumps(response["extra"], ensure_ascii=False)),
        str(response["riskLevel"]),
        str(response["detail"]).replace("|", ""),
        str(response["score"]),
        str(response["requestId"]),
        str(response["message"]).replace("|", ""),
    )
    return str(one_row)


def transfor_json(data_json, response):
    data_json = collections.defaultdict(handle, data_json)
    response = collections.defaultdict(handle, response)
    text_dict = {}
    text_dict["game_id"] = str(data_json["gameId"])
    text_dict["request_id"] = str(data_json["btId"])
    text_dict["timestamp"] = str(data_json["timestamp"])
    text_dict["token_id"] = str(data_json["tokenId"])
    text_dict["role_name"] = str(data_json["nickname"]).replace("'", "").replace("|", "").replace("\n", "")
    text_dict["text"] = str(data_json["text"]).replace("\r", "").replace("'", "").replace("|", "").replace("\n", "")
    text_dict["gameid"] = str(data_json["gameId"])
    text_dict["server_id"] = str(data_json["serverId"])
    text_dict["account_id"] = str(data_json["accountId"])
    text_dict["role_id"] = str(data_json["roleId"])
    text_dict["role_vip"] = str(data_json["vipLevel"])
    text_dict["role_level"] = str(data_json["level"])
    text_dict["ip"] = str(data_json["ip"])
    text_dict["channel"] = str(data_json["channel"])
    text_dict["relationship"] = str(data_json["relationship"])
    text_dict["target_id"] = str(data_json["targetId"])
    text_dict["union_id"] = str(data_json["organizationId"])
    text_dict["team_id"] = str(data_json["teamId"])
    text_dict["scene_id"] = str(data_json["sceneId"])
    text_dict["mac"] = str(data_json["mac"])
    text_dict["uuid"] = str(data_json["uuid"])
    text_dict["idfv"] = str(data_json["idfv"])
    text_dict["idfa"] = str(data_json["idfa"])
    text_dict["device_id"] = str(data_json["deviceId"])
    text_dict["phone"] = str(data_json["phone"])
    text_dict["imei"] = str(data_json["imei"])
    text_dict["title"] = str(data_json["title"]).replace("|", "")
    text_dict["topic"] = str(data_json["topic"]).replace("|", "")
    text_dict["nick_orc"] = str(data_json["nickocr"]).replace("|", "")
    text_dict["channel_id"] = str(data_json["channelId"])
    text_dict["total_pay_money"] = str(data_json["sumPay"])
    text_dict["register_datetime"] = str(data_json["logtime"])
    text_dict["register_date"] = str(data_json["logday"])
    text_dict["last_pay_datetime"] = str(data_json["lastPay"])
    text_dict["last_pay_date"] = str(data_json["lastPayDay"])
    text_dict["last_login_datetime"] = str(data_json["lastLogin"])
    text_dict["last_login_date"] = str(data_json["lastLoginDay"])
    text_dict["last_logout_datetime"] = str(data_json["lastLogout"])
    text_dict["last_logout_date"] = str(data_json["lastLogoutDay"])
    text_dict["device_type"] = str(data_json["deviceType"])
    text_dict["code"] = str(response["code"])
    text_dict["extra"] = str(json.dumps(response["extra"], ensure_ascii=False))
    text_dict["risk_level"] = str(response["riskLevel"])
    text_dict["detail"] = str(response["detail"]).replace("|", "")
    text_dict["score"] = str(response["score"])
    text_dict["response_id"] = str(response["requestId"])
    text_dict["message"] = str(response["message"]).replace("|", "")
    return text_dict


def handle():
    return ""
