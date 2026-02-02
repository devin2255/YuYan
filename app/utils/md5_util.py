import hashlib


def generate_md5(s: str) -> str:
    return hashlib.md5(s.encode(encoding="utf-8")).hexdigest()
