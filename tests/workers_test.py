import asyncio
import logging
import time

import pytest

from botflow.exceptions import PipelineExceptedError
from botflow.workers import AsyncLoopThreadWorker, PipelineWorker


def _wire_signals(worker: PipelineWorker):
    progress_events = []
    status_events = []
    error_events = []
    finished_events = []

    worker.progress.connect(lambda v: progress_events.append(v))
    worker.status.connect(lambda s: status_events.append(s))
    worker.error.connect(lambda e: error_events.append(e))
    worker.finished.connect(lambda d: finished_events.append(d))

    return progress_events, status_events, error_events, finished_events


@pytest.fixture
def logger():
    log = logging.getLogger('botflow-tests')
    log.setLevel(logging.DEBUG)
    return log


@pytest.fixture
def async_loop():
    loop = AsyncLoopThreadWorker()
    loop.start()
    yield loop
    loop.stop()
    time.sleep(0.05)


def test_pipeline_runs_sync_steps_and_emits_signals(async_loop, logger):
    ctx = {'value': 0}

    def step_one(context):
        context.data['value'] += 1
        context.pipeline_info.status('step_one running')
        context.pipeline_info.progress(10)

    def step_two(context):
        context.data['value'] += 2

    worker = PipelineWorker(
        ctx=ctx, pipeline=[step_one, step_two], logger=logger, async_loop=async_loop
    )
    progress, status, error, finished = _wire_signals(worker)
    worker.run()

    assert error == []
    assert finished == [ctx]
    assert ctx['value'] == 3

    assert 0 in progress
    assert 50 in progress
    assert 100 in progress

    assert any(s == 'Starting pipeline' for s in status)
    assert any(s.startswith('Step 1 of 2:') for s in status)
    assert any(s.startswith('Step 2 of 2:') for s in status)
    assert any(s == 'Pipeline completed successfully' for s in status)


def test_pipeline_runs_async_step(async_loop, logger):
    ctx = {'done': False}

    async def async_step(context):
        await asyncio.sleep(0)
        context.data['done'] = True

    worker = PipelineWorker(ctx=ctx, pipeline=[async_step], logger=logger, async_loop=async_loop)
    progress, status, error, finished = _wire_signals(worker)
    worker.run()

    assert error == []
    assert finished == [ctx]
    assert ctx['done'] is True
    assert 100 in progress
    assert any(s == 'Pipeline completed successfully' for s in status)


def test_pipeline_emits_popup_message_for_pipeline_excepted_error(async_loop, logger):
    ctx = {}

    def bad_step(_):
        raise PipelineExceptedError('internal message', popup_message='User-friendly message')

    worker = PipelineWorker(ctx=ctx, pipeline=[bad_step], logger=logger, async_loop=async_loop)
    _, _, error, finished = _wire_signals(worker)

    worker.run()

    assert finished == []
    assert len(error) == 1
    assert error[0] == 'User-friendly message'


def test_pipeline_emits_traceback_for_generic_exception(async_loop, logger):
    ctx = {}

    def bad_step(_):
        raise ValueError('boom')

    worker = PipelineWorker(ctx=ctx, pipeline=[bad_step], logger=logger, async_loop=async_loop)
    _, _, error, finished = _wire_signals(worker)

    worker.run()

    assert finished == []
    assert len(error) == 1
    assert 'ValueError' in error[0]
    assert 'boom' in error[0]
