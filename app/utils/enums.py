from enum import Enum


class ListTypeEnum(Enum):
    WHITELIST = 0
    SENSITIVE = 1
    IGNORE = 2

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.WHITELIST: "白名单",
            cls.SENSITIVE: "敏感词",
            cls.IGNORE: "忽略词",
        }
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {"白名单": cls.WHITELIST, "敏感词": cls.SENSITIVE, "忽略词": cls.IGNORE}
        return key_map[s]


class ListMatchRuleEnum(Enum):
    TEXT_AND_NAME = 0
    TEXT = 1
    ROLE_NAME = 2
    IP = 3
    SERVER_ID = 4
    ROLE_AND_SERVER_ID = 5
    ACCOUNT_ID = 6
    YOUZU_ID = 7
    FINGERPRINT_ID = 8

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.TEXT_AND_NAME.value: ["text", "nickname"],
            cls.TEXT.value: ["text"],
            cls.ROLE_NAME.value: ["nickname"],
            cls.IP.value: ["ip"],
            cls.SERVER_ID.value: ["server_id"],
            cls.ROLE_AND_SERVER_ID.value: ["role_id_and_server_id"],
            cls.ACCOUNT_ID.value: ["account_id"],
            cls.YOUZU_ID.value: ["youzu_id"],
            cls.FINGERPRINT_ID.value: ["fingerprint_id"],
        }
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {
            "文本加昵称": cls.TEXT_AND_NAME,
            "文本": cls.TEXT,
            "昵称": cls.ROLE_NAME,
            "ip": cls.IP,
            "server_id": cls.SERVER_ID,
            "serverId": cls.SERVER_ID,
            "role_id_and_server_id": cls.ROLE_AND_SERVER_ID,
            "RoleIdAndServerId": cls.ROLE_AND_SERVER_ID,
            "account_id": cls.ACCOUNT_ID,
            "accountId": cls.ACCOUNT_ID,
            "youzu_id": cls.YOUZU_ID,
            "youzuId": cls.YOUZU_ID,
            "fingerprint_id": cls.FINGERPRINT_ID,
            "fingerprintId": cls.FINGERPRINT_ID,
        }
        return key_map[s]

    @classmethod
    def enum2filtertext(cls, s, msg):
        key_map = {
            cls.TEXT_AND_NAME.value: [msg.text, msg.nickname],
            cls.TEXT.value: [msg.text],
            cls.ROLE_NAME.value: [msg.nickname],
            cls.IP.value: [msg.ip],
            cls.SERVER_ID.value: [msg.server_id],
            cls.ROLE_AND_SERVER_ID.value: ["{}_{}".format(msg.server_id, msg.role_id)],
            cls.ACCOUNT_ID.value: [msg.account_id],
            cls.YOUZU_ID.value: [msg.youzu_id],
            cls.FINGERPRINT_ID.value: [msg.fingerprint_id],
        }
        return key_map[int(s)]


class ListMatchTypeEnum(Enum):
    ALL = 1
    SEMANTIC = 2

    @classmethod
    def desc(cls, status):
        key_map = {cls.ALL: "原文匹配", cls.SEMANTIC: "语义匹配"}
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {"原文匹配": cls.ALL, "语义匹配": cls.SEMANTIC}
        return key_map[s]


class ListSuggestEnum(Enum):
    REJECT = 0
    PASS = 1
    REVIEW = 2

    @classmethod
    def desc(cls, status):
        key_map = {cls.REJECT: "拒绝", cls.PASS: "通过", cls.REVIEW: "审核"}
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {"拒绝": cls.REJECT, "通过": cls.PASS, "审核": cls.REVIEW}
        return key_map[s]


class ListRiskTypeEnum(Enum):
    NORMAL = 0
    POLITICS = 100
    PORN = 200
    ABUSE = 210
    AD = 300
    AD_PULL = 310
    BUMP = 400
    MEANINGLESS = 500
    PROHIBIT = 600
    OTHER = 700
    BLACK_ACCOUNT = 720
    BLACK_IP = 730
    HIGH_RISK_ACCOUNT = 800
    CUSTOM = 900
    NICKNAME_RISK = 910

    @classmethod
    def desc(cls, status):
        key_map = {
            cls.NORMAL.value: "正常",
            cls.POLITICS.value: "涉政",
            cls.PORN.value: "色情",
            cls.ABUSE.value: "辱骂",
            cls.AD.value: "广告",
            cls.AD_PULL.value: "防拉人",
            cls.BUMP.value: "灌水",
            cls.MEANINGLESS.value: "无意义",
            cls.PROHIBIT.value: "违禁",
            cls.OTHER.value: "其他",
            cls.BLACK_ACCOUNT.value: "黑账号",
            cls.BLACK_IP.value: "黑IP",
            cls.HIGH_RISK_ACCOUNT.value: "高危账号",
            cls.CUSTOM.value: "自定义",
            cls.NICKNAME_RISK.value: "昵称违规",
        }
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {
            "正常": cls.NORMAL,
            "涉政": cls.POLITICS,
            "色情": cls.PORN,
            "辱骂": cls.ABUSE,
            "广告": cls.AD,
            "防拉人": cls.AD_PULL,
            "灌水": cls.BUMP,
            "无意义": cls.MEANINGLESS,
            "违禁": cls.PROHIBIT,
            "其他": cls.OTHER,
            "黑账号": cls.BLACK_ACCOUNT,
            "黑IP": cls.BLACK_IP,
            "高危账号": cls.HIGH_RISK_ACCOUNT,
            "自定义": cls.CUSTOM,
            "昵称违规": cls.NICKNAME_RISK,
        }
        return key_map[s]

    @classmethod
    def yidun2enum(cls, s):
        key_map = {
            0: cls.NORMAL,
            500: cls.POLITICS,
            100: cls.PORN,
            600: cls.ABUSE,
            200: cls.AD,
            260: cls.AD,
            700: cls.BUMP,
            300: cls.PROHIBIT,
            400: cls.PROHIBIT,
            900: cls.OTHER,
            1100: cls.OTHER,
        }
        return key_map[s]

    @classmethod
    def wechat2enum(cls, s):
        key_map = {
            100: cls.NORMAL,
            20001: cls.POLITICS,
            20002: cls.PORN,
            20003: cls.ABUSE,
            10001: cls.AD,
            20008: cls.AD,
            20012: cls.ABUSE,
            20006: cls.PROHIBIT,
            21000: cls.OTHER,
            20013: cls.OTHER,
        }
        return key_map[s]


class ListStatusEnum(Enum):
    OFF = 0
    ON = 1

    @classmethod
    def desc(cls, status):
        key_map = {cls.OFF: "停用", cls.ON: "启用"}
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {"停用": cls.OFF, "启用": cls.ON}
        return key_map[s]


class SwichEnum(Enum):
    OFF = 0
    ON = 1

    @classmethod
    def desc(cls, status):
        key_map = {cls.OFF: "禁用", cls.ON: "启用"}
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {"禁用": cls.OFF, "启用": cls.ON}
        return key_map[s]


class SwitchEnum(Enum):
    OFF = 0
    ON = 1

    @classmethod
    def desc(cls, status):
        key_map = {cls.OFF: "禁用", cls.ON: "启用"}
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {"禁用": cls.OFF, "启用": cls.ON}
        return key_map[s]


class H5SDKIDEnum(Enum):
    WECHAT = 0
    DOUYIN = 1
    KUAISHOU = 2

    @classmethod
    def desc(cls, status):
        key_map = {cls.WECHAT: "0011000", cls.DOUYIN: "0011021", cls.KUAISHOU: "0011046"}
        return key_map[status]

    @classmethod
    def str2enum(cls, s):
        key_map = {"0011000": cls.WECHAT, "0011021": cls.DOUYIN, "0011046": cls.KUAISHOU}
        return key_map[s]

    @classmethod
    def user_id_prefix(cls, status):
        key_map = {cls.WECHAT: "0060042_", cls.DOUYIN: "0060498_", cls.KUAISHOU: "0060534_"}
        return key_map[status]
