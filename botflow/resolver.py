import sys
from pathlib import Path
from typing import Optional

from botflow.runtime import get_lib_resource_dir, get_user_resource_dir

USER_RESOUCES_DIR = 'user_resources'
LIB_RESOURCES_DIR = 'lib_resources'


def _bundle_root() -> Optional[Path]:
    meipass = getattr(sys, '_MEIPASS', None)
    return Path(meipass) if meipass else None


def find_resource_file(name: str) -> Path:
    bundle_root = _bundle_root()
    if bundle_root:
        for res_dir in (USER_RESOUCES_DIR, LIB_RESOURCES_DIR):
            if not (bundle_root / res_dir).is_dir():
                continue

            bundle_root_res_dir = bundle_root / res_dir
            candidate = bundle_root_res_dir / name

            if candidate.is_file():
                return candidate

        raise FileNotFoundError(f"Resource file '{name}' not found.")

    app_res_dir = get_user_resource_dir()
    if app_res_dir:
        candidate = app_res_dir / name
        if candidate.is_file():
            return candidate

    lib_res_dir = get_lib_resource_dir() / name
    if lib_res_dir.is_file():
        return Path(str(lib_res_dir))

    raise FileNotFoundError(f"Resource file '{name}' not found.")


def find_all_locales_dirs() -> list[Path]:
    locales_dirs = []
    bundle_root = _bundle_root()
    if bundle_root:
        for res_dir in (LIB_RESOURCES_DIR, USER_RESOUCES_DIR):
            if not (bundle_root / res_dir).is_dir():
                continue

            bundle_root_res_dir = bundle_root / res_dir
            candidate = bundle_root_res_dir / 'locales'

            if candidate.is_dir():
                locales_dirs.append(candidate)

        if not locales_dirs:
            raise FileNotFoundError('Locales directory not found.')

        return locales_dirs

    lib_locales_dir = get_lib_resource_dir() / 'locales'
    if lib_locales_dir.is_dir():
        locales_dirs.append(Path(str(lib_locales_dir)))

    app_res_dir = get_user_resource_dir()
    if app_res_dir:
        candidate = app_res_dir / 'locales'
        if candidate.is_dir():
            locales_dirs.append(candidate)

    if not locales_dirs:
        raise FileNotFoundError('Locales directory not found.')

    return locales_dirs
