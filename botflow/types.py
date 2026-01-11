import logging
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

from PySide6.QtWidgets import QWidget


@runtime_checkable
class I18n(Protocol):
    def t(self, key: str, **params: Any) -> str: ...


@dataclass(frozen=True)
class BotPipelineInfo:
    status: Optional[Callable[[str], None]]
    progress: Optional[Callable[[int], None]]
    percentage: int
    step_of: str
    step_name: str
    step_number: int
    total_steps: int


@dataclass(frozen=True)
class FinishContext:
    data: dict[str, Any]
    logger: logging.Logger
    pipeline_info: BotPipelineInfo


FinishReturn = Union[None, Awaitable[None]]
FinishFn = Callable[[FinishContext], FinishReturn]
Validator = Callable[[Any], tuple[bool, str]]


@dataclass(frozen=True)
class StepSpec(ABC):
    key: str
    title: str
    widget_cls: type['WidgetAbstract']
    validator: Optional[Validator] = field(default=None)


@dataclass(frozen=True)
class FlowSpec:
    name: str
    steps: list[StepSpec]
    on_finish: list[FinishFn] = field(default_factory=list)


class ABCQWidgetMeta(ABCMeta, type(QWidget)):
    pass


class LoadingAbstract(QWidget, metaclass=ABCQWidgetMeta):
    @abstractmethod
    def set_progress(self, value: int) -> None:  # noqa
        pass

    @abstractmethod
    def set_status(self, text: str) -> None:  # noqa
        pass


Spec = TypeVar('Spec', bound=StepSpec)


class WidgetAbstract(QWidget, Generic[Spec], metaclass=ABCQWidgetMeta):
    def __init__(self, spec: Spec, parent: Optional[QWidget] = None, **extra_kwargs: Any):
        super().__init__(parent)
        self.spec = spec
        self.extra_kwargs = extra_kwargs

    @abstractmethod
    def value(self) -> Any:
        pass
