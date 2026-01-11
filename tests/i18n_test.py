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


def test_from_locales_dirs_loads_single_dir_and_merges_files(monkeypatch, tmp_path: Path):
    locales_dir = tmp_path / 'locales'
    _write_json(locales_dir / 'pt-BR.json', {'common.start': 'Iniciar'})
    _write_json(locales_dir / 'en_US.json', {'common.start': 'Start'})

    import botflow.i18n as i18n_mod

    monkeypatch.setattr(i18n_mod, 'find_all_locales_dirs', lambda: str(locales_dir))

    i18n = I18n.from_locales_dirs('pt-BR')
    assert i18n.t('common.start') == 'Iniciar'

    i18n.set_lang('en_US')
    assert i18n.t('common.start') == 'Start'


def test_from_locales_dirs_accepts_list_of_dirs_and_user_overrides_lib(monkeypatch, tmp_path: Path):
    lib_dir = tmp_path / 'lib_locales'
    _write_json(lib_dir / 'pt-BR.json', {'common.start': 'Iniciar', 'common.back': 'Voltar'})

    user_dir = tmp_path / 'user_locales'
    _write_json(user_dir / 'pt-BR.json', {'common.start': 'Começar'})
    _write_json(user_dir / 'en_US.json', {'common.start': 'Start'})

    import botflow.i18n as i18n_mod

    monkeypatch.setattr(i18n_mod, 'find_all_locales_dirs', lambda: [str(lib_dir), str(user_dir)])

    i18n = I18n.from_locales_dirs('pt-BR')
    assert i18n.t('common.start') == 'Começar'
    assert i18n.t('common.back') == 'Voltar'

    i18n.set_lang('en_US')
    assert i18n.t('common.start') == 'Start'
