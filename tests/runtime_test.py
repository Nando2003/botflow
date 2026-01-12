from pathlib import Path
from unittest import mock

from botflow.runtime import get_lang, get_user_resource_dir


class TestGetResourceDir:
    def test_returns_path_when_resources_dir_is_set(self, monkeypatch):
        monkeypatch.setenv('BOTFLOW_RESOURCES_DIR', '/home/user/resources')
        with mock.patch('pathlib.Path.exists', return_value=True):
            result = get_user_resource_dir()
            assert isinstance(result, Path)
            assert result == Path('/home/user/resources').resolve()

    def test_returns_none_when_no_resources_dir_and_no_default(self, monkeypatch):
        monkeypatch.delenv('BOTFLOW_RESOURCES_DIR', raising=False)
        result = get_user_resource_dir()
        assert result is None

    def test_uses_default_when_resources_dir_not_set(self, monkeypatch):
        monkeypatch.delenv('BOTFLOW_RESOURCES_DIR', raising=False)
        with mock.patch('pathlib.Path.exists', return_value=True):
            result = get_user_resource_dir(default='/tmp/default')
            assert isinstance(result, Path)
            assert result == Path('/tmp/default').resolve()

    def test_expands_and_resolves_tilde_in_path(self, monkeypatch):
        monkeypatch.setenv('BOTFLOW_RESOURCES_DIR', '~/resources')
        with mock.patch('pathlib.Path.exists', return_value=True):
            result = get_user_resource_dir()
            assert isinstance(result, Path)
            assert '~' not in str(result)
            assert result.is_absolute()

    def test_accepts_path_object_as_default(self, monkeypatch):
        path_obj = Path('/tmp/resources')
        monkeypatch.delenv('BOTFLOW_RESOURCES_DIR', raising=False)
        with mock.patch('pathlib.Path.exists', return_value=True):
            result = get_user_resource_dir(default=path_obj)
            assert isinstance(result, Path)
            assert result == path_obj.resolve()

    def test_resources_dir_takes_precedence_over_default(self, monkeypatch):
        monkeypatch.setenv('BOTFLOW_RESOURCES_DIR', '/path/from/env')
        with mock.patch('pathlib.Path.exists', return_value=True):
            result = get_user_resource_dir(default='/path/from/default')
            assert result == Path('/path/from/env').resolve()


class TestGetLang:
    def test_returns_lang_from_environment_when_set(self, monkeypatch):
        monkeypatch.setenv('BOTFLOW_LANG', 'pt_BR')
        result = get_lang()
        assert result == 'pt_BR'

    def test_returns_system_locale_when_lang_not_set(self, monkeypatch):
        monkeypatch.delenv('BOTFLOW_LANG', raising=False)
        with mock.patch('botflow.runtime.getdefaultlocale', return_value=('en_US', 'UTF-8')):
            result = get_lang()
            assert result == 'en_US'

    def test_ignores_encoding_from_getdefaultlocale(self, monkeypatch):
        monkeypatch.delenv('BOTFLOW_LANG', raising=False)
        with mock.patch('botflow.runtime.getdefaultlocale', return_value=('pt_BR', 'UTF-8')):
            result = get_lang()
            assert result == 'pt_BR'
            assert 'UTF-8' not in str(result)

    def test_handles_none_locale_from_system(self, monkeypatch):
        monkeypatch.delenv('BOTFLOW_LANG', raising=False)
        with mock.patch('botflow.runtime.getdefaultlocale', return_value=(None, None)):
            result = get_lang()
            assert result is None

    def test_lang_from_environment_takes_precedence(self, monkeypatch):
        monkeypatch.setenv('BOTFLOW_LANG', 'es_ES')
        with mock.patch('botflow.runtime.getdefaultlocale', return_value=('en_US', 'UTF-8')):
            result = get_lang()
            assert result == 'es_ES'
