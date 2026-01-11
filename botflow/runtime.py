import importlib.resources as ir
from locale import getdefaultlocale
from pathlib import Path

import __main__


def get_user_resource_dir(default: str | Path | None = None) -> Path | None:
    val = getattr(__main__, 'RESOURCES_DIR', None)
    if val is None:
        if default is None:
            return None
        path = Path(default).expanduser().resolve()
        return path if path.exists() else None

    path = Path(val).expanduser().resolve()
    return path if path.exists() else None


def get_user_bundle_resource_dir(default: str | Path | None = None) -> Path | None:
    val = getattr(__main__, 'BUNDLE_RESOURCES_DIR', None)
    if val is None:
        if default is None:
            return None
        path = Path(default).expanduser().resolve()
        return path if path.exists() else None

    path = Path(val).expanduser().resolve()
    return path if path.exists() else None


def get_lang() -> str | None:
    val = getattr(__main__, 'LANG', None)
    if val is None:
        locale, _ = getdefaultlocale()
        return locale
    return val


def get_lib_resource_dir() -> Path:
    lib_res_dir = ir.files('botflow') / 'resources'
    return Path(str(lib_res_dir))
