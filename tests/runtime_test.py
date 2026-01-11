from pathlib import Path
from unittest import mock

from botflow.runtime import get_lang, get_user_resource_dir


class TestGetResourceDir:
    def test_returns_path_when_resources_dir_is_set(self):
        with mock.patch('__main__.RESOURCES_DIR', '/home/user/resources', create=True):
            with mock.patch('pathlib.Path.exists', return_value=True):
                result = get_user_resource_dir()
                assert isinstance(result, Path)
                assert result == Path('/home/user/resources').resolve()

    def test_returns_none_when_no_resources_dir_and_no_default(self):
        with mock.patch.dict('__main__.__dict__', {}, clear=False):
            if hasattr(__import__('__main__'), 'RESOURCES_DIR'):
                delattr(__import__('__main__'), 'RESOURCES_DIR')
            result = get_user_resource_dir()
            assert result is None

    def test_uses_default_when_resources_dir_not_set(self):
        with mock.patch('botflow.runtime.__main__', new_callable=lambda: mock.MagicMock(spec=[])):
            with mock.patch('pathlib.Path.exists', return_value=True):
                result = get_user_resource_dir(default='/tmp/default')
                assert isinstance(result, Path)
                assert result == Path('/tmp/default').resolve()

    def test_expands_and_resolves_tilde_in_path(self):
        with mock.patch('__main__.RESOURCES_DIR', '~/resources', create=True):
            with mock.patch('pathlib.Path.exists', return_value=True):
                result = get_user_resource_dir()
                assert isinstance(result, Path)
                assert '~' not in str(result)
                assert result.is_absolute()

    def test_accepts_path_object_as_default(self):
        path_obj = Path('/tmp/resources')
        with mock.patch('botflow.runtime.__main__', new_callable=lambda: mock.MagicMock(spec=[])):
            with mock.patch('pathlib.Path.exists', return_value=True):
                result = get_user_resource_dir(default=path_obj)
                assert isinstance(result, Path)
                assert result == path_obj.resolve()

    def test_resources_dir_takes_precedence_over_default(self):
        with mock.patch('__main__.RESOURCES_DIR', '/path/from/main', create=True):
            with mock.patch('pathlib.Path.exists', return_value=True):
                result = get_user_resource_dir(default='/path/from/default')
                assert result == Path('/path/from/main').resolve()


class TestGetLang:
    def test_returns_lang_from_main_when_set(self):
        with mock.patch('__main__.LANG', 'pt_BR', create=True):
            result = get_lang()
            assert result == 'pt_BR'

    def test_returns_system_locale_when_lang_not_set(self):
        with mock.patch('botflow.runtime.__main__', new_callable=lambda: mock.MagicMock(spec=[])):
            with mock.patch('botflow.runtime.getdefaultlocale', return_value=('en_US', 'UTF-8')):
                result = get_lang()
                assert result == 'en_US'

    def test_ignores_encoding_from_getdefaultlocale(self):
        with mock.patch('botflow.runtime.__main__', new_callable=lambda: mock.MagicMock(spec=[])):
            with mock.patch('botflow.runtime.getdefaultlocale', return_value=('pt_BR', 'UTF-8')):
                result = get_lang()
                assert result == 'pt_BR'
                assert 'UTF-8' not in str(result)

    def test_handles_none_locale_from_system(self):
        with mock.patch('botflow.runtime.__main__', new_callable=lambda: mock.MagicMock(spec=[])):
            with mock.patch('botflow.runtime.getdefaultlocale', return_value=(None, None)):
                result = get_lang()
                assert result is None

    def test_lang_from_main_takes_precedence(self):
        with mock.patch('__main__.LANG', 'es_ES', create=True):
            with mock.patch('botflow.runtime.getdefaultlocale', return_value=('en_US', 'UTF-8')):
                result = get_lang()
                assert result == 'es_ES'
