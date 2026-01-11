import asyncio
import inspect
import threading
import traceback
from logging import Logger
from typing import Any, Coroutine, List, Optional

from PySide6.QtCore import QObject, Signal, Slot

from botflow.exceptions import PipelineExceptedError
from botflow.types import BotPipelineInfo, FinishContext, FinishFn


class AsyncLoopThreadWorker:
    def __init__(self) -> None:
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._started = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        def _runner() -> None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self._started.set()
            self.loop.run_forever()

        self._thread = threading.Thread(target=_runner, daemon=True)
        self._thread.start()
        self._started.wait()

    def stop(self) -> None:
        if not self.loop:
            return
        self.loop.call_soon_threadsafe(self.loop.stop)

    def run(self, coro: Coroutine[Any, Any, Any]) -> Any:
        if not self.loop:
            raise RuntimeError('Async loop not started')
        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return fut.result()


class PipelineWorker(QObject):
    progress = Signal(int)
    status = Signal(str)
    error = Signal(str)
    finished = Signal(dict)

    def __init__(
        self,
        ctx: dict[str, Any],
        pipeline: List[FinishFn],
        logger: Logger,
        async_loop: AsyncLoopThreadWorker,
    ):
        super().__init__()
        self.ctx = ctx
        self.pipeline = pipeline
        self.logger = logger
        self.async_loop = async_loop
        self.async_loop.start()

    def _call_step(
        self,
        fn: FinishFn,
        progress_percentage: int,
        step_of: str,
        step_name: str,
        step_number: int,
        total_steps: int,
    ) -> None:
        context = FinishContext(
            data=self.ctx,
            logger=self.logger,
            pipeline_info=BotPipelineInfo(
                status=self.status.emit,
                progress=self.progress.emit,
                percentage=progress_percentage,
                step_of=step_of,
                step_name=step_name,
                step_number=step_number,
                total_steps=total_steps,
            ),
        )

        if inspect.iscoroutinefunction(fn):
            self.async_loop.run(fn(context))
            return

        fn(context)

    @Slot()
    def run(self):
        try:
            total = len(self.pipeline)
            self.logger.info('Starting pipeline with %d steps', total)

            self.progress.emit(0)
            self.status.emit('Starting pipeline')

            for i, fn in enumerate(self.pipeline, start=1):
                pct = int((i - 1) / total * 100)
                step_of = f'Step {i} of {total}:'
                step_name = f'{fn.__name__}'
                full_step_name = f'{step_of} {step_name}'
                step_number = i

                self.logger.info(full_step_name)
                self.status.emit(full_step_name)
                self.progress.emit(pct)

                self._call_step(fn, pct, step_of, step_name, step_number, total)

            self.status.emit('Pipeline completed successfully')
            self.progress.emit(100)

            self.logger.info('Pipeline completed successfully')
            self.finished.emit(self.ctx)
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.warning('Pipeline Error: %s', tb)

            if isinstance(e, PipelineExceptedError):
                popup_msg = e.popup_message
                self.error.emit(popup_msg)
            else:
                self.error.emit(tb)
