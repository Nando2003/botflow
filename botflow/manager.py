import os
from logging import Logger
from typing import Any, Optional

from PySide6.QtCore import QThread, Slot
from PySide6.QtGui import QCloseEvent, QIcon, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from botflow.i18n import I18n
from botflow.logger import configure_logger
from botflow.pages import InitialPage, LoadingPage
from botflow.qss import qss_to_string
from botflow.resolver import find_resource_file
from botflow.runtime import get_lang
from botflow.types import FinishFn, FlowSpec, LoadingAbstract, StepSpec, WidgetAbstract
from botflow.workers import AsyncLoopThreadWorker, PipelineWorker


class FlowManager(QWidget):
    ROOT_INITIAL = 'initial'
    ROOT_WIZARD = 'wizard'
    ROOT_LOADING = 'loading'

    def __init__(
        self,
        flow: FlowSpec,
        logger: Optional[Logger] = None,
        icon_path: Optional[str] = None,
    ):
        super().__init__()
        self.flow = flow
        self.logger = logger if logger else configure_logger()

        self.lang = get_lang() or 'en_US'
        self.i18n = I18n.from_locales_dirs(self.lang)

        self.context: dict[str, Any] = {}
        self.steps: list[StepSpec] = []
        self.pipeline: list[FinishFn] = []

        self._async_loop = AsyncLoopThreadWorker()
        self._async_loop.start()

        self._thread: Optional[QThread] = None
        self._worker: Optional[PipelineWorker] = None

        self._set_style()

        self.wizard_page = QWidget()
        self.wizard_page.setObjectName('wizard')
        self._wizard_layout = QVBoxLayout(self.wizard_page)

        self.stack = QStackedWidget()
        self.back_btn = QPushButton(self.i18n.t('common.back'))
        self.next_btn = QPushButton(self.i18n.t('common.next'))
        self.back_btn.setProperty('role', 'nav')
        self.next_btn.setProperty('role', 'primary')

        self.back_btn.clicked.connect(self.back)
        self.next_btn.clicked.connect(self.foward)

        if icon_path and os.path.exists(icon_path):
            qicon = QIcon(icon_path)
            self.setWindowIcon(qicon)

        self.initial_page = self.create_initial_page()
        self.loading_page = self.create_loading_page()

        self._build_wizard_ui()
        self.root_stack = QStackedWidget()
        self._root_pages: dict[str, int] = {}
        self.register_root_pages()

        layout = QVBoxLayout(self)
        layout.addWidget(self.root_stack)

        self.load_flow(self.flow)
        self.set_root_page(self.ROOT_INITIAL)

    def _set_style(self):
        style_file = find_resource_file('styles/flow_manager.qss')
        qss_string = qss_to_string(style_file)
        self.setStyleSheet(qss_string)

    def _build_wizard_ui(self) -> None:
        nav_container = QWidget()
        nav_container.setObjectName('nav_container')
        nav = QHBoxLayout(nav_container)
        nav.setContentsMargins(0, 0, 0, 0)
        nav.addWidget(self.back_btn)
        nav.addStretch()
        nav.addWidget(self.next_btn)

        nav_divider = QWidget()
        nav_divider.setObjectName('nav_divider')
        nav_divider.setFixedHeight(1)

        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addWidget(self.stack, 1)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._wizard_layout.addWidget(center_container, 1)

        self._wizard_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        )
        self._wizard_layout.addWidget(nav_divider, 0)
        self._wizard_layout.addSpacerItem(
            QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        )
        self._wizard_layout.addWidget(nav_container, 0)

    def create_initial_page(self) -> InitialPage:
        return InitialPage(self.flow.name, self.go_to_wizard_page, self.i18n)

    def create_loading_page(self) -> LoadingAbstract:
        return LoadingPage(self.i18n)

    def current_index(self) -> int:
        return self.stack.currentIndex()

    def current_spec(self) -> StepSpec:
        return self.steps[self.current_index()]

    def page_kwargs(self, spec: StepSpec) -> dict[str, Any]:
        return {'spec': spec, 'i18n': self.i18n}

    def make_page(self, spec: StepSpec):
        return spec.widget_cls(**self.page_kwargs(spec))

    def get_page_value(self, widget: WidgetAbstract) -> Any:
        return widget.value()

    def register_root_pages(self) -> None:
        self.add_root_page(self.ROOT_INITIAL, self.initial_page)
        self.add_root_page(self.ROOT_WIZARD, self.wizard_page)
        self.add_root_page(self.ROOT_LOADING, self.loading_page)

    def add_root_page(self, name: str, page: QWidget) -> int:
        idx = self.root_stack.addWidget(page)
        self._root_pages[name] = idx
        return idx

    def set_root_page(self, name: str) -> None:
        self.root_stack.setCurrentIndex(self._root_pages[name])

    def load_flow(self, flow: FlowSpec) -> None:
        self.context = {}
        self.pipeline = list(flow.on_finish)
        self.steps = list(flow.steps)
        self.rebuild_pages(go_to=0)

    def rebuild_pages(self, go_to: int = 0) -> None:
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
            w.deleteLater()

        for spec in self.steps:
            self.stack.addWidget(self.make_page(spec))

        self.stack.setCurrentIndex(max(0, min(go_to, self.stack.count() - 1)))
        self.update_nav()

    def update_nav(self) -> None:
        i = self.current_index()
        self.back_btn.setEnabled(i > 0)
        last = self.stack.count() > 0 and i == self.stack.count() - 1
        text = self.i18n.t('common.start') if last else self.i18n.t('common.next')
        self.next_btn.setText(text)

    def validate_step(self, spec: StepSpec, value: Any) -> tuple[bool, str]:
        if spec.validator:
            return spec.validator(value)
        return True, ''

    def confirm_run(self) -> bool:
        reply = QMessageBox(self)
        reply.setWindowTitle(self.i18n.t('dialogs.confirm.title'))
        reply.setText(self.i18n.t('dialogs.confirm.run_pipeline_text'))

        yes_button = reply.addButton(
            self.i18n.t('dialogs.confirm.yes'), QMessageBox.ButtonRole.YesRole
        )
        no_button = reply.addButton(
            self.i18n.t('dialogs.confirm.no'), QMessageBox.ButtonRole.NoRole
        )
        reply.setDefaultButton(no_button)
        reply.setIcon(QMessageBox.Icon.Question)
        reply.exec()

        return reply.clickedButton() == yes_button

    def show_warn(self, msg: str) -> None:
        QMessageBox.warning(self, self.i18n.t('dialogs.warn_title'), msg)

    def show_success(self, msg: str) -> None:
        QMessageBox.information(self, self.i18n.t('dialogs.success_title'), msg)

    def show_error(self, msg: str) -> None:
        QMessageBox.critical(self, self.i18n.t('dialogs.error_title'), msg)

    def back(self) -> None:
        i = self.current_index()
        if i > 0:
            self.stack.setCurrentIndex(i - 1)
            self.update_nav()

    def foward(self) -> None:
        spec = self.current_spec()
        page = self.stack.currentWidget()
        val = self.get_page_value(page) if isinstance(page, WidgetAbstract) else None

        ok, err = self.validate_step(spec, val)
        if not ok:
            self.show_warn(err)
            return

        self.context[spec.key] = val

        if self.current_index() == self.stack.count() - 1:
            can_run = self.confirm_run()

            if not can_run:
                return

            self.run_pipeline_threaded()
            return

        self.stack.setCurrentIndex(self.current_index() + 1)
        self.update_nav()

    def run_pipeline_threaded(self) -> None:
        if not self.pipeline:
            self.show_success(self.i18n.t('messages.no_pipeline'))
            return

        self.next_btn.setEnabled(False)
        self.back_btn.setEnabled(False)

        self.set_root_page(self.ROOT_LOADING)

        ctx_copy = self.context.copy()

        self._thread = QThread(self)
        self._worker = PipelineWorker(ctx_copy, self.pipeline, self.logger, self._async_loop)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.loading_page.set_progress)
        self._worker.status.connect(self.loading_page.set_status)
        self._worker.finished.connect(self.on_finished)
        self._worker.error.connect(self.on_error)

        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    @Slot(dict)
    def on_finished(self, ctx: dict[str, Any]) -> None:
        self.context.update(ctx)
        self.next_btn.setEnabled(True)
        self.back_btn.setEnabled(True)
        self.show_success(self.i18n.t('messages.flow_success'))
        self.restart_to_beginning()

    @Slot(str)
    def on_error(self, error_msg: str) -> None:
        self.next_btn.setEnabled(True)
        self.back_btn.setEnabled(True)
        prefix = self.i18n.t('messages.flow_error_prefix')
        self.show_error(prefix + error_msg)
        self.restart_to_beginning()

    def restart_to_beginning(self) -> None:
        self.load_flow(self.flow)
        self.set_root_page(self.ROOT_WIZARD)

    def go_to_wizard_page(self) -> None:
        self.set_root_page(self.ROOT_WIZARD)

    def closeEvent(self, event: QCloseEvent):  # noqa: N802
        if not event.spontaneous():
            event.accept()
            return

        reply = QMessageBox(self)
        reply.setWindowTitle(self.i18n.t('dialogs.close.title'))
        reply.setText(self.i18n.t('dialogs.close.exit_text'))
        yes_button = reply.addButton(
            self.i18n.t('dialogs.confirm.yes'), QMessageBox.ButtonRole.YesRole
        )
        no_button = reply.addButton(
            self.i18n.t('dialogs.confirm.no'), QMessageBox.ButtonRole.NoRole
        )
        reply.setDefaultButton(no_button)
        reply.setIcon(QMessageBox.Icon.Question)

        reply.exec()

        if reply.clickedButton() != yes_button:
            event.ignore()
            return

        event.accept()
