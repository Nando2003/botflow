from typing import Callable

from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QMovie
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from botflow.qss import qss_to_string
from botflow.resolver import find_resource_file
from botflow.types import I18n, LoadingAbstract


class InitialPage(QWidget):
    def __init__(self, name: str, on_start: Callable, i18n: I18n):
        super().__init__()
        style_file = find_resource_file('styles/initial_page.qss')
        qss_string = qss_to_string(style_file)
        self.setStyleSheet(qss_string)

        title_label = QLabel(name)
        title_label.setProperty('role', 'initial_title')
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        row_container = QWidget()
        row_container.setLayout(row)

        start_text = i18n.t('common.start') if i18n else 'Start'
        start_btn = QPushButton(start_text)
        start_btn.setProperty('role', 'initial_button')
        start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if on_start:
            start_btn.clicked.connect(on_start)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addStretch()
        main_layout.addWidget(row_container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacerItem(
            QSpacerItem(
                0,
                58,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Fixed,
            )
        )
        main_layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()


class LoadingPage(LoadingAbstract):
    def __init__(self, i18n: I18n):
        super().__init__()
        style_file = find_resource_file('styles/loading_page.qss')
        qss_string = qss_to_string(style_file)
        self.setStyleSheet(qss_string)

        loading_gif = find_resource_file('assets/loading.gif')
        gif_label = QLabel(self)
        gif_label.setProperty('role', 'loading_icon')
        movie = QMovie(loading_gif.as_posix())
        movie.setScaledSize(QSize(64, 64))
        gif_label.setMovie(movie)
        movie.start()

        title_text = i18n.t('loading.title') if i18n else 'In Progress...'
        title_lbl = QLabel(title_text, self)
        title_lbl.setProperty('role', 'loading_title')

        header = QHBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(gif_label)
        header.addSpacing(5)
        header.addWidget(title_lbl)

        self.status_lbl = QLabel('', self)
        self.status_lbl.setProperty('role', 'loading_status')

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setProperty('role', 'loading_progress')

        progress_col = QVBoxLayout()
        progress_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_col.setSpacing(6)
        progress_col.addWidget(self.status_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        progress_col.addWidget(self.progress_bar)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 24, 0, 0)
        layout.addLayout(header)
        layout.addSpacerItem(
            QSpacerItem(0, 32, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        )
        layout.addLayout(progress_col)
        layout.addStretch()

    @Slot(int)
    def set_progress(self, value: int):
        self.progress_bar.setValue(max(0, min(value, 100)))

    @Slot(str)
    def set_status(self, text: str):
        self.status_lbl.setText(text)
