import datetime, decimal
from collections.abc import Mapping, Iterable
import json


def find_strict_non_serializables(obj, path="root"):
    non_serializables = []

    def check(o, p):
        try:
            json.dumps(o)
            return
        except Exception:
            pass  # ادامه بده و بررسی کن

        # اگر map هست
        if isinstance(o, Mapping):
            for k, v in o.items():
                check(v, f"{p}.{k}")
        # اگر iterable (نه str/bytes)
        elif isinstance(o, Iterable) and not isinstance(o, (str, bytes)):
            for i, item in enumerate(o):
                check(item, f"{p}[{i}]")
        else:
            non_serializables.append(f"{p}: {type(o).__name__}")

    check(obj, path)
    return non_serializables