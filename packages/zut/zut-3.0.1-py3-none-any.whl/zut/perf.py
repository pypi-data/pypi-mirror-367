"""
Measurement of elapsed time and memory consumption.
"""
from __future__ import annotations

import logging
from time import time_ns
from types import FunctionType
from typing import TYPE_CHECKING, NamedTuple, overload

if TYPE_CHECKING:
    from typing import Literal
    from psutil import Process

from zut import get_logger

_logger = get_logger(__name__)


_process_info = None
_process_info_initiated = False

@overload
def _get_process_info(*, force: Literal[True]) -> Process:
    ...

@overload
def _get_process_info(*, force: Literal[False] = False) -> Process|None:
    ...

def _get_process_info(*, force = False) -> Process|None:
    global _process_info, _process_info_initiated

    if not _process_info_initiated:
        try:
            from psutil import Process
            _process_info = Process()
        except ModuleNotFoundError:
            pass
        _process_info_initiated = True

    if force and _process_info is None:
        raise ModuleNotFoundError(name='psutil')

    return _process_info


TrackingInfo = NamedTuple('TrackStart', [('time', float), ('memory', int|None)])

@overload
def get_tracking_info(*, force: Literal[True], level = logging.DEBUG) -> TrackingInfo:
    ...

@overload
def get_tracking_info(*, force: Literal[False] = False, level = logging.DEBUG) -> TrackingInfo|None:
    ...

def get_tracking_info(*, force = False, level = logging.DEBUG) -> TrackingInfo|None:
    if not force:
        if not _logger.isEnabledFor(level):
            return None
    
    process = _get_process_info()
    memory = process.memory_info().rss if process is not None else None
    time = time_ns()
    return TrackingInfo(time, memory)


def log_tracking_elapsed(start: TrackingInfo|None, *, prefix: str|None = None, level = logging.DEBUG):
    if start is None:
        return # tracking is disabled (e.g. tracking logging level is not enabled)
    
    end = get_tracking_info(force=True)

    message = f'{prefix} ' if prefix else 'elapsed: '
    
    elapsed_time = (end.time - start.time) / 1e9
    if elapsed_time >= 10*1e-3:
        message += f"{elapsed_time:,.3f} s"
    else:
        message += f"{elapsed_time*1e3:,.6f} ms"

    if start.memory is not None and end.memory is not None:
        elapsed_memory = end.memory - start.memory
        if elapsed_memory > 1024**2:
            message += f", {elapsed_memory/1024**2:,.1f} MiB ({start.memory:,.0f} -> {end.memory:,.0f} B)"
        elif elapsed_memory > 1024:
            message += f", {elapsed_memory/1024:,.1f} kiB ({start.memory:,.0f} -> {end.memory:,.0f} B)"
        else:
            message += f", {elapsed_memory:,.0f} B ({start.memory:,.0f} -> {end.memory:,.0f} B)"

    _logger.log(level, message)


def track(func: FunctionType|None = None, *, force = False, level = logging.DEBUG):
    """
    A decorator to track performance of a function.
    """
    def decorator(func: FunctionType):
        def wrapper(*args, **kwargs):
            start = get_tracking_info(force=force, level=level)
            result = func(*args, **kwargs)
            log_tracking_elapsed(start, prefix=f"{func.__name__}:", level=level)
            return result
        
        return wrapper
    
    if func is not None: # decorated without params
        return decorator(func)
    else: # decorated with params
        return decorator
