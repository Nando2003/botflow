import sys
from pathlib import Path
from typing import Optional

from botflow.runtime import (
    get_lib_resource_dir,
    get_user_bundle_resource_dir,
    get_user_resource_dir,
)

LIB_BUNDLE_RESOURCES_DIR = 'lib_resources'


def _bundle_root() -> Optional[Path]:
    meipass = getattr(sys, '_MEIPASS', None)
    return Path(meipass) if meipass else None


def find_resource_file(name: str) -> Path:
    bundle_root = _bundle_root()
    if bundle_root:
        res_dirs = []

        bundle_user_res_dir = get_user_bundle_resource_dir()
        if bundle_user_res_dir:
            res_dirs.append(bundle_user_res_dir)

        res_dirs.append(bundle_root / LIB_BUNDLE_RESOURCES_DIR)

        for res_dir in res_dirs:
            if not res_dir.is_dir():
                continue

            candidate = res_dir / name

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
        return lib_res_dir

    raise FileNotFoundError(f"Resource file '{name}' not found.")


def _find_bundle_locales_dirs() -> list[Path]:
    bundle_locales_dirs = []
    bundle_root = _bundle_root()
    if not bundle_root:
        return bundle_locales_dirs

    bundle_res_dirs = []

    bundle_user_res_dir = get_user_bundle_resource_dir()
    if bundle_user_res_dir:
        bundle_res_dirs.append(bundle_user_res_dir)

    bundle_res_dirs.append(bundle_root / LIB_BUNDLE_RESOURCES_DIR)

    for res_dir in bundle_res_dirs:
        if not res_dir.is_dir():
            continue

        candidate = res_dir / 'locales'
        if candidate.is_dir():
            bundle_locales_dirs.append(candidate)

    return bundle_locales_dirs


def find_all_locales_dirs() -> list[Path]:
    locales_dirs = _find_bundle_locales_dirs()
    if locales_dirs:
        return locales_dirs

    lib_locales_dir = get_lib_resource_dir() / 'locales'
    if lib_locales_dir.is_dir():
        locales_dirs.append(lib_locales_dir)

    app_res_dir = get_user_resource_dir()
    if app_res_dir:
        candidate = app_res_dir / 'locales'
        if candidate.is_dir():
            locales_dirs.append(candidate)

    if not locales_dirs:
        raise FileNotFoundError('Locales directory not found.')

    return locales_dirs
