try:
    from PyInstaller.building.datastruct import Tree
except ImportError as e:
    raise RuntimeError('This hook requires PyInstaller to be installed.') from e

from botflow.resolver import LIB_RESOURCES_DIR, USER_RESOUCES_DIR
from botflow.runtime import get_lib_resource_dir, get_user_resource_dir

datas = []

user_dir = get_user_resource_dir()
if user_dir and user_dir.exists():
    datas += Tree(user_dir.as_posix(), prefix=f'botflow/{USER_RESOUCES_DIR}')

lib_dir = get_lib_resource_dir()
if lib_dir and lib_dir.exists():
    datas += Tree(lib_dir.as_posix(), prefix=f'botflow/{LIB_RESOURCES_DIR}')
