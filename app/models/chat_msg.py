class ChatMsg(object):
    def __init__(
        self,
        text="",
        token_id=None,
        nickname=None,
        ip=None,
        bt_id=None,
        channel=None,
        relationship=None,
        target_id=None,
        app_id=None,
        server_id=None,
        role_id=None,
        request_id=None,
        channel_id=None,
        openid=None,
        openkey=None,
        type="APP",
        youzu_id="",
        account_id="",
        fingerprint_id="",
        timestamp=None,
        chat_history="",
        sdk_conf_id=None,
        sdk_id=None,
    ):
        self.text = text
        self.token_id = token_id
        self.nickname = nickname
        self.ip = ip
        self.bt_id = bt_id
        self.channel = channel
        self.relationship = relationship
        self.target_id = target_id
        self.app_id = app_id
        self.type = type
        self.server_id = server_id
        self.role_id = role_id
        self.request_id = request_id
        self.youzu_id = youzu_id
        self.account_id = account_id
        self.fingerprint_id = fingerprint_id
        self.channel_id = channel_id
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
