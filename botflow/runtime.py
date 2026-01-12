import importlib.resources as ir
import os
from locale import getdefaultlocale
from pathlib import Path


def get_user_resource_dir(default: str | Path | None = None) -> Path | None:
    val = os.getenv('BOTFLOW_RESOURCES_DIR')
    if not val:
        val = default
    if val is None:
        return None

    p = Path(val).expanduser()
    return p.resolve() if p.exists() else None

def get_user_bundle_resource_dir(default: str | Path | None = None) -> Path | None:
    val = os.getenv('BOTFLOW_BUNDLE_RESOURCES_DIR')
    if not val:
        val = default
    if val is None:
        return None

    p = Path(val).expanduser()
    return p.resolve() if p.exists() else None

def get_lang() -> str | None:
    val = os.getenv('BOTFLOW_LANG')
    if val:
        return val
    locale, _ = getdefaultlocale()
    return locale


def get_lib_resource_dir() -> Path:
    lib_res_dir = ir.files('botflow') / 'resources'
    return Path(str(lib_res_dir))
