class ChatMsg(object):
    def __init__(
        self,
        text="",
        tokenId=None,
        nickname=None,
        ip=None,
        btId=None,
        channel=None,
        relationship=None,
        targetId=None,
        gameId=None,
        serverId=None,
        roleId=None,
        requestId=None,
        channelId=None,
        openid=None,
        openkey=None,
        type="GAME",
        youzuId="",
        accountId="",
        fingerprintId="",
        timestamp=None,
        chat_history="",
        sdk_conf_id=None,
        sdk_id=None,
    ):
        self.text = text
        self.tokenId = tokenId
        self.nickname = nickname
        self.ip = ip
        self.btId = btId
        self.channel = channel
        self.relationship = relationship
        self.targetId = targetId
        self.gameId = gameId
        self.type = type
        self.serverId = serverId
        self.roleId = roleId
        self.requestId = requestId
        self.youzuId = youzuId
        self.accountId = accountId
        self.fingerprintId = fingerprintId
        self.channelId = channelId
        self.openid = openid
        self.openkey = openkey
        self.sdk_conf_id = sdk_conf_id
        self.sdk_id = sdk_id
        self.timestamp = timestamp
        self.chat_history = chat_history

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != "type":
                setattr(self, key, value)
