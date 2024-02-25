
from typing import List


class FlutterIncorrectTranslationKey(Exception):
    def __init__(self, key: str) -> None:
        super().__init__(f"Incorrect translation key \"{key}\"")
        self.key = key

class FlutterTranslateHasNoKeys(Exception):
    def __init__(self, keys: List[str]) -> None:
        super().__init__(f"Translation has no keys (" + ", ".join([f"\"{k}\"" for k in keys]) + ")")
        self.keys = keys
