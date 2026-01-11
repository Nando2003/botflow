from pathlib import Path
from unittest import mock

import pytest

from botflow.resolver import LIB_RESOURCES_DIR, USER_RESOUCES_DIR, _bundle_root, find_resource_file


class TestBundleRoot:
    def test_returns_path_when_meipass_is_set(self):
        with mock.patch.dict('sys.__dict__', {'_MEIPASS': '/path/to/bundle'}):
            result = _bundle_root()
            assert isinstance(result, Path)
            assert result == Path('/path/to/bundle')

    def test_returns_none_when_meipass_not_set(self):
        with mock.patch('sys._MEIPASS', None, create=True):
            result = _bundle_root()
            assert result is None

    def test_returns_none_by_default(self):
        result = _bundle_root()
        assert result is None or isinstance(result, Path)


class TestFindResourceFile:
    def test_finds_file_in_app_resources_when_bundled(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        app_resources = bundle_root / USER_RESOUCES_DIR
        app_resources.mkdir(parents=True)
        resource_file = app_resources / 'config.json'
        resource_file.write_text('{}')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            result = find_resource_file('config.json')
            assert result == resource_file

    def test_finds_file_in_lib_resources_when_bundled(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        app_resources = bundle_root / USER_RESOUCES_DIR
        app_resources.mkdir(parents=True)
        lib_resources = bundle_root / LIB_RESOURCES_DIR
        lib_resources.mkdir(parents=True)
        resource_file = lib_resources / 'theme.qss'
        resource_file.write_text('')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            result = find_resource_file('theme.qss')
            assert result == resource_file

    def test_raises_when_not_bundled(self):
        with mock.patch('botflow.resolver._bundle_root', return_value=None):
            with pytest.raises(FileNotFoundError, match="Resource file 'any.txt' not found."):
                find_resource_file('any.txt')

    def test_raises_when_bundled_but_no_resources_dir(self):
        with mock.patch('botflow.resolver._bundle_root', return_value=Path('/nonexistent')):
            with pytest.raises(FileNotFoundError, match="Resource file 'missing.txt' not found."):
                find_resource_file('missing.txt')

    def test_raises_when_not_bundled_and_no_fallback(self):
        with mock.patch('botflow.resolver._bundle_root', return_value=None):
            with pytest.raises(FileNotFoundError, match="Resource file 'notfound.txt' not found."):
                find_resource_file('notfound.txt')

    def test_prefers_user_resources_over_lib_resources(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        app_resources = bundle_root / USER_RESOUCES_DIR
        app_resources.mkdir(parents=True)
        lib_resources = bundle_root / LIB_RESOURCES_DIR
        lib_resources.mkdir(parents=True)

        app_file = app_resources / 'config.json'
        lib_file = lib_resources / 'config.json'
        app_file.write_text('app')
        lib_file.write_text('lib')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            result = find_resource_file('config.json')
            assert result == app_file

    def test_prefers_bundled_over_user_defined_dir(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        app_resources = bundle_root / USER_RESOUCES_DIR
        app_resources.mkdir(parents=True)
        bundled_file = app_resources / 'resource.txt'
        bundled_file.write_text('bundled')

        user_dir = tmp_path / 'user'
        user_dir.mkdir()
        user_file = user_dir / 'resource.txt'
        user_file.write_text('user')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            with mock.patch('botflow.resolver.get_user_resource_dir', return_value=user_dir):
                result = find_resource_file('resource.txt')
                assert result == bundled_file

    def test_returns_path_object(self, tmp_path):
        app_resources = tmp_path / USER_RESOUCES_DIR
        app_resources.mkdir(parents=True)
        resource_file = app_resources / 'test.txt'
        resource_file.write_text('test')

        with mock.patch('botflow.resolver._bundle_root', return_value=tmp_path):
            result = find_resource_file('test.txt')
            assert isinstance(result, Path)
            assert result.is_file()

    def test_handles_nested_file_paths(self, tmp_path):
        app_resources = tmp_path / USER_RESOUCES_DIR
        nested_dir = app_resources / 'subdir'
        nested_dir.mkdir(parents=True)
        resource_file = nested_dir / 'nested.json'
        resource_file.write_text('{}')

        with mock.patch('botflow.resolver._bundle_root', return_value=tmp_path):
            result = find_resource_file('subdir/nested.json')
            assert result == resource_file
