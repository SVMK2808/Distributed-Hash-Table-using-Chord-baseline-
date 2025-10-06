from typing import Optional

class Storage:
    def __init__(self):
        # in-memory single-owner store
        self._store = {}

    def put(self, key: str, value: str):
        self._store[key] = value
        return True

    def get(self, key: str) -> Optional[str]:
        return self._store.get(key)

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def dump(self):
        return dict(self._store)
