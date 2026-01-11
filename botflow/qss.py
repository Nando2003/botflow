from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def qss_to_string(*paths: PathLike) -> str:
    parts: list[str] = []

    for p in paths:
        p = Path(p)

        if p.suffix != '.qss':
            raise ValueError('File must have a .qss extension.')

        if not p.is_file():
            raise FileNotFoundError(f'The file {p} does not exist.')

        parts.append(p.read_text(encoding='utf-8'))

    return '\n'.join(parts) + '\n'
