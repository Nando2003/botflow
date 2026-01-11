import json
from pathlib import Path
from typing import Any

from botflow.resolver import find_all_locales_dirs


class I18n:
    def __init__(self, catalog: dict[str, Any], lang: str, fallback_lang: str = 'en_US'):
        self.catalog = catalog
        self.lang = lang
        self.fallback_lang = fallback_lang

    def t(self, key: str, **params: Any) -> str:
        loc = self.lang or self.fallback_lang

        bucket = self.catalog.get(loc, {})
        v = bucket.get(key)

        if v is None and self.fallback_lang and self.fallback_lang != loc:
            v = self.catalog.get(self.fallback_lang, {}).get(key)

        if v is None:
            raise KeyError(f'Missing translation key: {key} (lang={self.lang})')

        if not isinstance(v, str):
            return str(v)

        return v.format(**params) if params else v

    def set_lang(self, lang: str) -> None:
        self.lang = lang

    @staticmethod
    def from_locales_dirs(lang: str):
        locales_dirs = find_all_locales_dirs()
        catalog: dict[str, dict[str, Any]] = {}

        for locales_dir in locales_dirs if isinstance(locales_dirs, list) else [locales_dirs]:
            for json_file in Path(locales_dir).glob('*.json'):
                locale_name = json_file.stem

                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if locale_name not in catalog:
                    catalog[locale_name] = {}

                catalog[locale_name].update(data)

        return I18n(catalog, lang)
