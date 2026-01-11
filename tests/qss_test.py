from pathlib import Path

import pytest

from botflow.qss import qss_to_string


def test_qss_to_string_reads_one_file_and_adds_trailing_newline(tmp_path: Path):
    p = tmp_path / 'a.qss'
    p.write_text('QWidget { color: red; }', encoding='utf-8')

    out = qss_to_string(p)

    assert out == 'QWidget { color: red; }\n'


def test_qss_to_string_reads_multiple_files_in_order(tmp_path: Path):
    a = tmp_path / 'a.qss'
    b = tmp_path / 'b.qss'
    a.write_text('A', encoding='utf-8')
    b.write_text('B', encoding='utf-8')

    out = qss_to_string(a, b)

    assert out == 'A\nB\n'


def test_qss_to_string_rejects_non_qss_extension(tmp_path: Path):
    p = tmp_path / 'a.txt'
    p.write_text('x', encoding='utf-8')

    with pytest.raises(ValueError, match=r'\.qss'):
        qss_to_string(p)


def test_qss_to_string_raises_if_file_does_not_exist(tmp_path: Path):
    p = tmp_path / 'missing.qss'

    with pytest.raises(FileNotFoundError, match='does not exist'):
        qss_to_string(p)


def test_qss_to_string_accepts_str_paths(tmp_path: Path):
    p = tmp_path / 'a.qss'
    p.write_text('X', encoding='utf-8')

    out = qss_to_string(str(p))

    assert out == 'X\n'
