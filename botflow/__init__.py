from botflow.manager import FlowManager
from botflow.types import FlowSpec
from botflow.widgets import (
    FileStepSpec,
    FileWidget,
    FormInput,
    FormStepSpec,
    FormWidget,
    TextStepSpec,
    TextWidget,
)

__all__ = [
    'FlowManager',
    'FileStepSpec',
    'FileWidget',
    'FormInput',
    'FormStepSpec',
    'FormWidget',
    'TextStepSpec',
    'TextWidget',
    'FlowSpec',
]

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


def get_hook_dirs():
    return [str(Path(__file__).resolve().with_name('_pyinstaller_hooks'))]


def run_application():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    return app


def run_flow_manager(
    flow_manager: FlowManager,
    *,
    width: int = 720,
    height: int = 300,
    window_title: str = 'Flow Manager',
):
    app = run_application()
    flow_manager.resize(width, height)
    flow_manager.setWindowTitle(window_title)
    flow_manager.show()
    sys.exit(app.exec())
