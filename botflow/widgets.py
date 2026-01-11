from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from botflow.qss import qss_to_string
from botflow.resolver import find_resource_file
from botflow.types import StepSpec, WidgetAbstract


class TextWidget(WidgetAbstract['TextStepSpec']):
    def __init__(self, spec: 'TextStepSpec', **extra_kwargs: Any) -> None:
        super().__init__(spec, **extra_kwargs)
        style_file = find_resource_file('styles/text_widget.qss')
        qss_string = qss_to_string(style_file)
        self.setStyleSheet(qss_string)

        title = QLabel(spec.title)
        title.setProperty('role', 'text_title')
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        help_label = None
        if spec.help_text.strip():
            help_label = QLabel(spec.help_text)
            help_label.setProperty('role', 'file_text_help')
            help_label.setWordWrap(True)
            help_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.input = QLineEdit()
        self.input.setProperty('role', 'text_input')
        self.input.setPlaceholderText(spec.placeholder)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.input)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(content)
        wrapper_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(wrapper)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(title)

        if help_label is not None:
            layout.addItem(QSpacerItem(0, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
            layout.addWidget(help_label)

        layout.addItem(QSpacerItem(0, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        layout.addWidget(scroll, 1)

    def value(self) -> str:
        return self.input.text().strip()


class FormWidget(WidgetAbstract['FormStepSpec']):
    def __init__(self, spec: 'FormStepSpec', **extra_kwargs) -> None:
        super().__init__(spec, **extra_kwargs)
        self._inputs: dict[str, QLineEdit] = {}

        style_file = find_resource_file('styles/form_widget.qss')
        qss_string = qss_to_string(style_file)
        self.setStyleSheet(qss_string)

        title = QLabel(spec.title)
        title.setProperty('role', 'step_title')
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)

        for inp in spec.inputs:
            lbl = QLabel(inp.label)
            lbl.setProperty('role', 'form_label')

            edit = QLineEdit()
            edit.setProperty('role', 'form_input')
            edit.setPlaceholderText(inp.placeholder)
            edit.setMaxLength(inp.max_length)
            edit.setEchoMode(inp.echo_mode)

            self._inputs[inp.key] = edit
            form.addRow(lbl, edit)

        content_layout.addLayout(form)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(content)
        wrapper_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(wrapper)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(title)
        layout.addItem(QSpacerItem(0, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        layout.addWidget(scroll, 1)

    def value(self) -> dict[str, str]:
        return {k: w.text().strip() for k, w in self._inputs.items()}


class FileWidget(WidgetAbstract['FileStepSpec']):
    def __init__(self, spec: 'FileStepSpec', **extra_kwargs: Any):
        super().__init__(spec, **extra_kwargs)
        style_file = find_resource_file('styles/file_widget.qss')
        qss_string = qss_to_string(style_file)
        self.setStyleSheet(qss_string)

        title = QLabel(spec.title)
        title.setProperty('role', 'file_title')
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        help_label = None
        if spec.help_text.strip():
            help_label = QLabel(spec.help_text)
            help_label.setProperty('role', 'file_text_help')
            help_label.setWordWrap(True)
            help_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.input = QLineEdit()
        self.input.setProperty('role', 'file_input')
        self.input.setReadOnly(True)
        self.input.setPlaceholderText('Nenhum arquivo selecionado')

        btn = QPushButton('Procurar')
        btn.setProperty('role', 'browse_button')
        btn.clicked.connect(self.pick)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(self.input, 1)
        row.addWidget(btn)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addLayout(row)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(content)
        wrapper_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # só horizontal
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(wrapper)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(title)

        if help_label is not None:
            layout.addItem(QSpacerItem(0, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
            layout.addWidget(help_label)

        layout.addItem(QSpacerItem(0, 12, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        layout.addWidget(scroll, 1)

    def pick(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.spec.dialog_title, filter=self.spec.file_filter
        )
        if path:
            self.input.setText(path)

    def value(self) -> str:
        return self.input.text().strip()


@dataclass(frozen=True)
class TextStepSpec(StepSpec):
    help_text: str = field(default='')
    placeholder: str = field(default='')
    widget_cls: type[WidgetAbstract] = field(default=TextWidget)


@dataclass(frozen=True)
class FormInput:
    key: str
    label: str
    placeholder: str = field(default='')
    max_length: int = field(default=255)
    echo_mode: QLineEdit.EchoMode = field(default=QLineEdit.EchoMode.Normal)


@dataclass(frozen=True)
class FormStepSpec(StepSpec):
    inputs: list[FormInput] = field(default_factory=list)
    widget_cls: type[WidgetAbstract] = field(default=FormWidget)


@dataclass(frozen=True)
class FileStepSpec(StepSpec):
    help_text: str = field(default='')
    dialog_title: str = field(default='Select a file')
    file_filter: str = field(default='All Files (*)')
    widget_cls: type[WidgetAbstract] = field(default=FileWidget)
