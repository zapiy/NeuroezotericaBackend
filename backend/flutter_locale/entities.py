from typing import TYPE_CHECKING, Dict, Set, Optional
from dataclasses import dataclass

from .errors import *
import re
if TYPE_CHECKING:
    from .manager import FlutterTranslationManager

CURLY_BRACKET_REGEX = re.compile(r'\{([^{}]+)\}')


class FlutterTranslateTemplate:
    def __init__(
        self, translate: str, *,
        description: Optional[str] = None
    ) -> None:
        self.translate = translate
        self.description = description
        self.keys: Optional[Set[str]] = (
            set(CURLY_BRACKET_REGEX.findall(translate))
            if "{" in translate and "}" in translate else
            None    
        )

class FlutterTranslate:
    def __init__(self, preview_name: str = None) -> None:
        self.preview_name: str = preview_name
        self._translations: Dict[str, str] = {}
        self._manager: 'FlutterTranslationManager' = None
    
    @property
    def readonly(self):
        return (not self._manager)
    
    @classmethod
    def from_manager(cls, manager: 'FlutterTranslationManager'):
        obj = cls()
        obj._manager = manager
        return obj
    
    def to_json(self):
        if self.readonly: return None
        return {
            "preview_name": self.preview_name,
            "translations": self._translations
        }
    
    @classmethod
    def from_json(cls, manager: 'FlutterTranslationManager', json: dict):
        if not {"preview_name", "translations"}.issubset(json.keys()):
            return cls()
        obj = cls.from_manager(manager)
        obj.preview_name = json.get("preview_name")
        obj._translations = json.get("translations")
        return obj
    
    def translate(self, key: str, translate: str = None):
        if self.readonly: return
        
        if key not in self._manager.definions:
            raise FlutterIncorrectTranslationKey(key)
        
        elif not translate:
            return self._translations.get(key)
        
        translation = self._manager.definions[key]
        if translation.keys:
            word_keys = CURLY_BRACKET_REGEX.findall(translate)
            if not translation.keys.issubset(word_keys):
                raise FlutterTranslateHasNoKeys(translation.keys.difference(word_keys))
        
        self._translations[key] = translate

    @property
    def completed_translations(self):
        if self.readonly: return None
        return {
            k: v.translate
            for k, v in self._manager.definions.items()
            if k in self._translations
        }
        
    @property
    def expected_translations(self):
        if self.readonly: return None
        return {
            k: v.translate
            for k, v in self._manager.definions.items()
            if k not in self._translations
        }


@dataclass
class FlutterLocale:
    code: str
    preview_name: str
    available: bool = False
    readonly: bool = False
