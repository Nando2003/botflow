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


def _search_for_file_in_bundle(filepath: str) -> Optional[Path]:
    bundle_root = _bundle_root()
    if not bundle_root:
        return None

    bundle_usr_resource_dir = get_user_bundle_resource_dir() or get_user_resource_dir()
    bundle_usr_resource_dir = (
        bundle_root / bundle_usr_resource_dir if bundle_usr_resource_dir else None
    )

    bundle_lib_resource_dir = bundle_root / LIB_BUNDLE_RESOURCES_DIR
    all_bundle_resource_dirs = [d for d in (bundle_usr_resource_dir, bundle_lib_resource_dir) if d]

    for res_dir in all_bundle_resource_dirs:
        if res_dir.is_dir():
            candidate = res_dir / filepath

            if candidate.is_file():
                return candidate

    return None


def _search_for_file_in_app(filepath: str) -> Optional[Path]:
    app_res_dir = get_user_resource_dir()
    lib_res_dir = get_lib_resource_dir()
    all_app_resource_dirs = [d for d in (app_res_dir, lib_res_dir) if d]

    for res_dir in all_app_resource_dirs:
        candidate = res_dir / filepath
        if candidate.is_file():
            return candidate

    return None


def find_resource_file(filepath: str) -> Path:
    bundle_file = _search_for_file_in_bundle(filepath)

    if bundle_file:
        return bundle_file

    app_file = _search_for_file_in_app(filepath)
    if app_file:
        return app_file

    raise FileNotFoundError(f"Resource file '{filepath}' not found.")


def _find_first_subfolder(subfolder: str, *directory: Path) -> list[Path]:
    result = []
    for res_dir in directory:
        if res_dir.is_dir():
            for item in res_dir.rglob(subfolder):
                if item.is_dir():
                    result.append(item)
                    break
    return result


def find_all_subfolder_by_name(subfolder: str) -> list[Path]:
    bundle_root = _bundle_root()

    if bundle_root:
        bundle_usr_resource_dir = get_user_bundle_resource_dir() or get_user_resource_dir()
        bundle_usr_resource_dir = (
            bundle_root / bundle_usr_resource_dir if bundle_usr_resource_dir else None
        )

        bundle_lib_resource_dir = bundle_root / LIB_BUNDLE_RESOURCES_DIR
        all_bundle_resource_dirs = [
            d for d in (bundle_lib_resource_dir, bundle_usr_resource_dir) if d
        ]
        return _find_first_subfolder(subfolder, *all_bundle_resource_dirs)

    app_res_dir = get_user_resource_dir()
    lib_res_dir = get_lib_resource_dir()
    all_app_resource_dirs = [d for d in (lib_res_dir, app_res_dir) if d]
    return _find_first_subfolder(subfolder, *all_app_resource_dirs)
