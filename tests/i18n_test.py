import json
from pathlib import Path

import pytest

from botflow.i18n import I18n


def _write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')


def test_t_returns_translation_for_locale():
    i18n = I18n(
        catalog={
            'pt-BR': {'common.start': 'Iniciar'},
            'en_US': {'common.start': 'Start'},
        },
        lang='pt-BR',
        fallback_lang='en_US',
    )

    assert i18n.t('common.start') == 'Iniciar'


def test_t_falls_back_to_default_locale_when_key_missing_in_locale():
    i18n = I18n(
        catalog={
            'pt-BR': {},
            'en_US': {'common.start': 'Start'},
        },
        lang='pt-BR',
        fallback_lang='en_US',
    )

    assert i18n.t('common.start') == 'Start'


def test_t_falls_back_to_default_locale_when_locale_missing():
    i18n = I18n(
        catalog={
            'en_US': {'common.start': 'Start'},
        },
        lang='pt-BR',
        fallback_lang='en_US',
    )

    assert i18n.t('common.start') == 'Start'


def test_t_returns_key_when_missing_everywhere():
    i18n = I18n(
        catalog={
            'en_US': {'common.back': 'Back'},
        },
        lang='pt-BR',
        fallback_lang='en_US',
    )

    with pytest.raises(KeyError, match='Missing translation key: common.start'):
        i18n.t('common.start')


def test_t_uses_default_locale_when_locale_is_none():
    i18n = I18n(
        catalog={
            'en_US': {'common.start': 'Start'},
        },
        lang='pt-BR',
        fallback_lang='en_US',
    )

    assert i18n.t('common.start') == 'Start'


def test_detects_duplicate_keys_with_different_values_in_pt_br_locale():
    locales_dir = Path(__file__).parent.parent / 'botflow' / 'resources' / 'locales' / 'pt_BR'

    all_keys = {}
    duplicates_with_different_values = []

    for json_file in locales_dir.glob('*.json'):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for key, value in data.items():
            if key in all_keys:
                if all_keys[key]['value'] != value:
                    duplicates_with_different_values.append(
                        {
                            'key': key,
                            'file1': all_keys[key]['file'],
                            'value1': all_keys[key]['value'],
                            'file2': json_file.name,
                            'value2': value,
                        }
                    )
            else:
                all_keys[key] = {'value': value, 'file': json_file.name}
    assert len(duplicates_with_different_values) == 0, (
        f'Found {len(duplicates_with_different_values)} duplicate keys with different values: '
        f'{duplicates_with_different_values}'
    )
