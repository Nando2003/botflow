from pathlib import Path
from unittest import mock

import pytest

from botflow.resolver import (
    LIB_BUNDLE_RESOURCES_DIR,
    _bundle_root,
    find_all_subfolder_by_name,
    find_resource_file,
)


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
        app_resources = tmp_path / 'user_bundle'
        app_resources.mkdir(parents=True)
        resource_file = app_resources / 'config.json'
        resource_file.write_text('{}')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            with mock.patch(
                'botflow.resolver.get_user_bundle_resource_dir', return_value=app_resources
            ):
                result = find_resource_file('config.json')
                assert result == resource_file

    def test_finds_file_in_lib_resources_when_bundled(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        lib_resources = bundle_root / LIB_BUNDLE_RESOURCES_DIR
        lib_resources.mkdir(parents=True)
        resource_file = lib_resources / 'theme.qss'
        resource_file.write_text('')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            with mock.patch('botflow.resolver.get_user_bundle_resource_dir', return_value=None):
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
        app_resources = tmp_path / 'user_bundle'
        app_resources.mkdir(parents=True)
        lib_resources = bundle_root / LIB_BUNDLE_RESOURCES_DIR
        lib_resources.mkdir(parents=True)

        app_file = app_resources / 'config.json'
        lib_file = lib_resources / 'config.json'
        app_file.write_text('app')
        lib_file.write_text('lib')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            with mock.patch(
                'botflow.resolver.get_user_bundle_resource_dir', return_value=app_resources
            ):
                result = find_resource_file('config.json')
                assert result == app_file

    def test_prefers_bundled_over_user_defined_dir(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        app_resources = tmp_path / 'user_bundle'
        app_resources.mkdir(parents=True)
        bundled_file = app_resources / 'resource.txt'
        bundled_file.write_text('bundled')

        user_dir = tmp_path / 'user'
        user_dir.mkdir()
        user_file = user_dir / 'resource.txt'
        user_file.write_text('user')

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            with mock.patch(
                'botflow.resolver.get_user_bundle_resource_dir', return_value=app_resources
            ):
                result = find_resource_file('resource.txt')
                assert result == bundled_file

    def test_returns_path_object(self, tmp_path):
        app_resources = tmp_path / 'user_bundle'
        app_resources.mkdir(parents=True)
        resource_file = app_resources / 'test.txt'
        resource_file.write_text('test')

        with mock.patch('botflow.resolver._bundle_root', return_value=tmp_path):
            with mock.patch(
                'botflow.resolver.get_user_bundle_resource_dir', return_value=app_resources
            ):
                result = find_resource_file('test.txt')
                assert isinstance(result, Path)
                assert result.is_file()

    def test_handles_nested_file_paths(self, tmp_path):
        app_resources = tmp_path / 'user_bundle'
        nested_dir = app_resources / 'subdir'
        nested_dir.mkdir(parents=True)
        resource_file = nested_dir / 'nested.json'
        resource_file.write_text('{}')

        with mock.patch('botflow.resolver._bundle_root', return_value=tmp_path):
            with mock.patch(
                'botflow.resolver.get_user_bundle_resource_dir', return_value=app_resources
            ):
                result = find_resource_file('subdir/nested.json')
                assert result == resource_file

    def test_user_resource_takes_precedence_over_lib_when_not_bundled(self, tmp_path):
        user_dir = tmp_path / 'user'
        user_dir.mkdir(parents=True)
        lib_dir = tmp_path / 'lib'
        lib_dir.mkdir(parents=True)

        user_file = user_dir / 'config.json'
        lib_file = lib_dir / 'config.json'
        user_file.write_text('user')
        lib_file.write_text('lib')

        with mock.patch('botflow.resolver._bundle_root', return_value=None):
            with mock.patch('botflow.resolver.get_user_resource_dir', return_value=user_dir):
                with mock.patch('botflow.resolver.get_lib_resource_dir', return_value=lib_dir):
                    result = find_resource_file('config.json')
                    assert result == user_file
                    assert result.read_text() == 'user'


class TestFindAllSubfolderByName:
    def test_finds_subfolder_in_user_and_lib_when_bundled(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        user_bundle = tmp_path / 'user_bundle'
        locales_user = user_bundle / 'locales'
        locales_user.mkdir(parents=True)

        lib_bundle = bundle_root / LIB_BUNDLE_RESOURCES_DIR
        locales_lib = lib_bundle / 'locales'
        locales_lib.mkdir(parents=True)

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            with mock.patch(
                'botflow.resolver.get_user_bundle_resource_dir', return_value=user_bundle
            ):
                result = find_all_subfolder_by_name('locales')
                assert len(result) == 2
                assert locales_user in result
                assert locales_lib in result

    def test_finds_nested_subfolder_recursively(self, tmp_path):
        bundle_root = tmp_path / 'bundle'
        lib_bundle = bundle_root / LIB_BUNDLE_RESOURCES_DIR
        nested_locales = lib_bundle / 'subdir' / 'locales'
        nested_locales.mkdir(parents=True)

        with mock.patch('botflow.resolver._bundle_root', return_value=bundle_root):
            with mock.patch('botflow.resolver.get_user_bundle_resource_dir', return_value=None):
                result = find_all_subfolder_by_name('locales')
                assert len(result) == 1
                assert nested_locales in result

    def test_lib_subfolder_appears_before_user_when_not_bundled(self, tmp_path):
        user_dir = tmp_path / 'user'
        user_locales = user_dir / 'locales'
        user_locales.mkdir(parents=True)

        lib_dir = tmp_path / 'lib'
        lib_locales = lib_dir / 'locales'
        lib_locales.mkdir(parents=True)

        with mock.patch('botflow.resolver._bundle_root', return_value=None):
            with mock.patch('botflow.resolver.get_user_resource_dir', return_value=user_dir):
                with mock.patch('botflow.resolver.get_lib_resource_dir', return_value=lib_dir):
                    result = find_all_subfolder_by_name('locales')
                    assert len(result) == 2
                    # Lib subfolder should come first
                    assert result[0] == lib_locales
                    assert result[1] == user_locales

    def test_returns_empty_list_when_subfolder_not_found(self, tmp_path):
        with mock.patch('botflow.resolver._bundle_root', return_value=None):
            with mock.patch('botflow.resolver.get_user_resource_dir', return_value=None):
                with mock.patch('botflow.resolver.get_lib_resource_dir', return_value=tmp_path):
                    result = find_all_subfolder_by_name('nonexistent')
                    assert result == []

    def test_stops_at_first_subfolder_found_in_each_directory(self, tmp_path):
        user_dir = tmp_path / 'user'
        locales1 = user_dir / 'locales'
        locales2 = user_dir / 'subdir' / 'locales'
        locales1.mkdir(parents=True)
        locales2.mkdir(parents=True)

        with mock.patch('botflow.resolver._bundle_root', return_value=None):
            with mock.patch('botflow.resolver.get_user_resource_dir', return_value=user_dir):
                with mock.patch('botflow.resolver.get_lib_resource_dir', return_value=None):
                    result = find_all_subfolder_by_name('locales')
                    assert len(result) == 1
                    assert result[0] in [locales2, locales1]
