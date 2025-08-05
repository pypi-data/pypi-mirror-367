"""
Common wrappers over `subprocess.run`.
"""
from __future__ import annotations

import logging
import os
import subprocess
from queue import Queue
from signal import Signals
from threading import Thread
from typing import (IO, TYPE_CHECKING, Any, Callable, Mapping, Sequence,
                    overload)

from zut import Color, SudoNotAvailable, get_logger, is_sudo_available

if TYPE_CHECKING:
    from typing import Literal


@overload
def run_process(cmd: str|os.PathLike|bytes|list[str|os.PathLike|bytes], *, encoding: Literal['bytes'], capture_output: bool|Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, sudo = False, shell = False, env: Mapping[str,Any]|None = None, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, input: str|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess[bytes]:
    ...

@overload
def run_process(cmd: str|os.PathLike|bytes|list[str|os.PathLike|bytes], *, encoding: Literal['utf-8', 'cp1252', 'unknown']|None = None, capture_output: bool|Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, sudo = False, shell = False, env: Mapping[str,Any]|None = None, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, input: str|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess[str]:
    ...

def run_process(cmd: str|os.PathLike|bytes|list[str|os.PathLike|bytes], *, encoding: str|Literal['unknown','bytes']|None = None, capture_output: bool|Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, sudo = False, shell = False, env: Mapping[str,Any]|None = None, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, input: str|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess:
    if sudo:
        if not is_sudo_available():
            raise SudoNotAvailable()
        if isinstance(cmd, str):
            cmd = f'sudo {cmd}'
        elif not isinstance(cmd, list):
            cmd = ['sudo', cmd]
        else:
            cmd = ['sudo', *cmd]

    if capture_output is None:
        capture_output = (stdout and stdout != 'disable') or (stderr and stderr != 'disable')

    cp = subprocess.run(cmd,
                        capture_output=True if capture_output else False,
                        text=encoding not in {'unknown', 'bytes'},
                        encoding=encoding if encoding not in {'unknown', 'bytes'} else None,
                        shell=shell,
                        env=env,
                        stdout=subprocess.DEVNULL if stdout == 'disable' else None,
                        stderr=subprocess.DEVNULL if stderr == 'disable' else None,
                        input=input)
    
    if encoding == 'unknown':
        def parse_unknown_encoding(output: bytes):
            if output is None:
                return None
            try:
                return output.decode('utf-8')
            except UnicodeDecodeError:
                return output.decode('cp1252')
        
        cp.stdout = parse_unknown_encoding(cp.stdout)
        cp.stderr = parse_unknown_encoding(cp.stderr)
    
    return verify_run_process(cp, strip=capture_output if capture_output is True or isinstance(capture_output, str) else None, check=check, stdout=stdout, stderr=stderr, logger=logger)


def verify_run_process(cp: subprocess.CompletedProcess, *, strip: Literal['rstrip-newline','strip',True]|None = None, check: int|Sequence[int]|bool = False, stdout: Literal['disable','raise','warning','error']|None = None, stderr: Literal['disable','raise','warning','error']|None = None, logger: logging.Logger|None = None) -> subprocess.CompletedProcess:
    if strip:
        cp.stdout = _strip_data(cp.stdout, strip)
        cp.stderr = _strip_data(cp.stderr, strip)
    
    invalid_returncode = False
    if check:
        if check is True:
            check = 0
        invalid_returncode = not (cp.returncode in check if not isinstance(check, int) else cp.returncode == check)

    invalid_stdout = stdout == 'raise' and cp.stdout
    invalid_stderr = stderr == 'raise' and cp.stderr

    if cp.stdout:
        level = None
        if stdout == 'warning':
            level = logging.WARNING
        elif stdout == 'error':
            level = logging.ERROR
        if level:
            (logger or get_logger(__name__)).log(level, f"{Color.PURPLE}[stdout]{Color.RESET} %s", stdout)
            
    if cp.stderr:
        level = None
        if stderr == 'warning':
            level = logging.WARNING
        elif stderr == 'error':
            level = logging.ERROR
        if level:
            (logger or get_logger(__name__)).log(level, f"{Color.PURPLE}[stderr]{Color.RESET} %s", stderr)

    if invalid_returncode or invalid_stdout or invalid_stderr:
        raise RunProcessError(cp.returncode, cp.args, cp.stdout, cp.stderr)    
    return cp


def run_process_callback(cmd: str|os.PathLike|bytes|Sequence[str|os.PathLike|bytes], *, encoding: str|Literal['unknown','bytes']|None = None, shell = False, env: Mapping[str,Any]|None = None, on_stdout: Callable[[str|bytes],None]|None = None, on_stderr: Callable[[str|bytes],None]|None = None, strip: Literal['rstrip-newline','strip',True]|None = None, strip_stderr: Literal['rstrip-newline','strip',True]|None = None) -> int:
    """
    Run a process, using `on_stdout` and/or `on_stderr` in other threads when data is available.
    """
    # See: https://stackoverflow.com/a/60777270
    queue = Queue()

    def enqueue_stream(stream: IO[str], source: str):
        for data in iter(stream.readline, ''):
            queue.put((source, data))
        stream.close()

    def enqueue_process(proc: subprocess.Popen):
        returncode = proc.wait()
        queue.put(('process', returncode))
    
    proc = subprocess.Popen(cmd,
                        text=encoding not in {'unknown', 'bytes'},
                        encoding=encoding if encoding not in {'unknown', 'bytes'} else None,
                        shell=shell,
                        env=env,
                        stdout=subprocess.PIPE if on_stdout else subprocess.DEVNULL,
                        stderr=subprocess.PIPE if on_stderr else subprocess.DEVNULL)
    
    if on_stdout:
        Thread(target=enqueue_stream, args=[proc.stdout, 'stdout'], daemon=True).start()
    if on_stderr:
        Thread(target=enqueue_stream, args=[proc.stderr, 'stderr'], daemon=True).start()
    Thread(target=enqueue_process, args=[proc], daemon=True).start()

    if strip_stderr is None:
        strip_stderr = strip
    
    while True:
        source, data = queue.get()
        if source == 'stdout':
            if on_stdout:
                on_stdout(_strip_data(data, strip))
        elif source == 'stderr':
            if on_stderr:
                on_stderr(_strip_data(data, strip_stderr))
        else: # process
            return data # returncode


def _strip_data(data, strip: Literal['rstrip-newline','strip',True]|None):
    if not strip:
        return data
    
    if isinstance(data, str):
        if strip == 'rstrip-newline':
            return data.rstrip('\r\n')
        elif strip == 'rstrip':
            return data.rstrip()
        else:
            return data.strip()
    else:
        raise TypeError(f"Cannot strip data of type {type(data).__name__}")         


class RunProcessError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, stdout, stderr):
        super().__init__(returncode, cmd, stdout, stderr)
        self.maxlen: int|None = 200
        self._message = None

    def with_maxlen(self, maxlen: int|None):
        self.maxlen = maxlen
        return self

    @property
    def message(self):
        if self._message is None:
            self._message = ''

            if self.returncode and self.returncode < 0:
                try:
                    self._message += "died with %r" % Signals(-self.returncode)
                except ValueError:
                    self._message += "died with unknown signal %d" % -self.returncode
            else:
                self._message += "returned exit code %d" % self.returncode

            if self.output:
                info = self.output[0:self.maxlen] + '…' if self.maxlen is not None and len(self.output) > self.maxlen else self.stdout
                self._message += ('\n' if self._message else '') + f"[stdout] {info}"

            if self.stderr:
                info = self.stderr[0:self.maxlen] + '…' if self.maxlen is not None and len(self.stderr) > self.maxlen else self.stderr
                self._message += ('\n' if self._message else '') + f"[stderr] {info}"

            self._message = f"Command '{self.cmd}' {self._message}"

        return self._message

    def __str__(self):
        return self.message
