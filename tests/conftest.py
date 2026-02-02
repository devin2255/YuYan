from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from yuyan.app import main as main_module


class DummySettings:
    def __init__(self, data):
        self._data = data

    def as_dict(self):
        return self._data


class DummyKafkaLog:
    def __init__(self, *args, **kwargs):
        return None

    def write_msg(self, msg):
        return None

    def write_query(self, msg):
        return None

    def write_json(self, msg):
        return None

    def write_img(self, msg):
        return None


class FakeACTree:
    def __init__(self, wordlist=None):
        self.words = set()
        if wordlist:
            for word, _ in wordlist:
                self.words.add(word)

    def add_word(self, word, value=None):
        self.words.add(word)

    def remove_word(self, word):
        self.words.discard(word)

    def make_automaton(self):
        return self

    def iter(self, text):
        return iter([])


class FakeRedis:
    def __init__(self):
        self._sets = {}
        self._hashes = {}
        self._zsets = {}
        self._strings = {}

    def smembers(self, key):
        return set(self._sets.get(key, set()))

    def sadd(self, key, *members):
        self._sets.setdefault(key, set()).update(str(m) for m in members)

    def srem(self, key, member):
        self._sets.setdefault(key, set()).discard(str(member))

    def hgetall(self, key):
        return dict(self._hashes.get(key, {}))

    def hget(self, key, field):
        return self._hashes.get(key, {}).get(field)

    def hset(self, key, field=None, value=None, mapping=None, **kwargs):
        if mapping is None:
            mapping = {}
            if field is not None:
                mapping[field] = value
            mapping.update(kwargs)
        self._hashes.setdefault(key, {}).update(mapping)

    def hmset(self, key, mapping):
        self.hset(key, mapping=mapping)

    def hdel(self, key, field):
        if key in self._hashes:
            self._hashes[key].pop(field, None)

    def hexists(self, key, field):
        return field in self._hashes.get(key, {})

    def exists(self, key):
        return key in self._sets or key in self._hashes or key in self._zsets or key in self._strings

    def zadd(self, key, mapping):
        self._zsets.setdefault(key, {})
        for member, score in mapping.items():
            self._zsets[key][member] = float(score)

    def zcount(self, key, min, max):
        data = self._zsets.get(key, {})
        return sum(1 for score in data.values() if float(min) <= score <= float(max))

    def zrevrangebyscore(self, key, min, max):
        data = self._zsets.get(key, {})
        filtered = [(member, score) for member, score in data.items() if float(min) <= score <= float(max)]
        filtered.sort(key=lambda item: item[1], reverse=True)
        return [item[0] for item in filtered]

    def zremrangebyscore(self, key, min, max):
        data = self._zsets.get(key, {})
        for member, score in list(data.items()):
            if float(min) <= score <= float(max):
                data.pop(member, None)

    def scan_iter(self):
        keys = set(self._sets.keys()) | set(self._hashes.keys()) | set(self._zsets.keys()) | set(self._strings.keys())
        return iter(keys)

    def get(self, key):
        return self._strings.get(key)

    def set(self, key, value):
        self._strings[key] = value


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def client(monkeypatch, tmp_path, fake_redis):
    black_file = Path(tmp_path / "black_client_ip.txt")
    black_file.write_text("1.1.1.1\n", encoding="utf-8")

    settings_data = {
        "ENVIRONMENT": "test",
        "COUNTRY": "zh",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        "REDIS_URL": "redis://fake/0",
        "CHAT_LOG_REDIS_URL": "redis://fake/1",
        "LOG": {
            "LEVEL": "DEBUG",
            "DIR": "logs/output",
            "SIZE_LIMIT": 1024 * 1024,
            "REQUEST_LOG": False,
            "FILE": False,
        },
        "LANGUAGE_SWITCH": False,
        "TIME_SEED": 0,
        "AD_DETECT_URL": "http://example.invalid",
        "LANGUAGE_CLS_URL": "http://example.invalid",
        "BLACK_CLIENT_IP_FILE": str(black_file),
    }

    fake_redis.sadd("all_games", "1001")
    fake_redis.hset("access_key", "1001", "test_key")
    fake_redis.hset("dun_secret", "1001", json.dumps({"secret_id": "sid", "secret_key": "skey"}))

    monkeypatch.setattr(main_module.redis.Redis, "from_url", lambda *args, **kwargs: fake_redis)
    monkeypatch.setattr(main_module, "KafkaLog", DummyKafkaLog)
    monkeypatch.setattr(main_module, "load_settings", lambda: DummySettings(settings_data))

    fake_builder = lambda wordlist: FakeACTree(wordlist)
    from yuyan.app.utils import ahocorasick_utils
    from yuyan.app.services import list_detail_service

    monkeypatch.setattr(ahocorasick_utils, "build_actree", fake_builder)
    monkeypatch.setattr(list_detail_service, "build_actree", fake_builder)

    app = main_module.create_app()
    with TestClient(app) as test_client:
        ctx = test_client.app.state.ctx
        ctx.config["BLACK_CLIENT_IP"] = ["1.1.1.1"]
        yield test_client
