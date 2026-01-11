from pathlib import Path

from PyInstaller.utils.hooks import get_module_file_attribute

module_path = get_module_file_attribute('botflow')
if module_path:
    botflow_dir = Path(module_path).parent
    datas = [(str(botflow_dir / 'resources'), 'lib_resources')]
else:
    datas = []
