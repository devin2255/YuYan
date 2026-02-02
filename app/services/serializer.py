from typing import Any


def to_dict(obj: Any):
    if isinstance(obj, list):
        return [item.to_dict() if hasattr(item, "to_dict") else dict(item) for item in obj]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return dict(obj)
