from typing import override, Optional
from os.path import join as join_path, abspath, normpath, sep
from collections import defaultdict

import os
import select
import logging

from .inotify import (
    Inotify, PollInotify,
    InotifyEvent,
    TerminalEventException,
    IN_CLOEXEC, IN_NONBLOCK,
    IN_MOVED_TO, IN_MOVED_FROM, IN_CREATE,
    IN_MOVE_SELF, IN_DELETE_SELF,
    IN_MASK_ADD, IN_MASK_CREATE,
    IN_ISDIR, IN_IGNORED,
    IN_Q_OVERFLOW, IN_UNMOUNT,
    IN_ALL_EVENTS,
    inotify_rm_watch,
    _check_return,
    get_inotify_event_names,
    __version__,
)

from .__main__ import _parse_mask, flags

_logger = logging.getLogger(__name__)

__all__ = (
    'TreeNotify',
    'PollTreeNotify',
)

class TreeNotify(Inotify):
    __slots__ = (
        '_masks',
    )

    _masks: dict[int, int]

    def __init__(self, flags: int = IN_CLOEXEC) -> None:
        super().__init__(flags)
        self._masks = defaultdict(int)

    @override
    def add_watch(self, path: str, mask: int = IN_ALL_EVENTS) -> int:
        path = normpath(abspath(path))
        self_mask = mask | IN_MOVED_TO | IN_MOVED_FROM | IN_CREATE
        add_watch = super().add_watch
        wd = add_watch(path, self_mask)

        if mask & IN_MASK_ADD:
            self._masks[wd] |= mask
        else:
            self._masks[wd] = mask

        child_mask = (mask & ~(IN_DELETE_SELF | IN_MOVE_SELF)) | IN_MOVED_TO | IN_MOVED_FROM | IN_CREATE
        for dirpath, dirnames, filenames in os.walk(path):
            for dirname in dirnames:
                child_path = join_path(dirpath, dirname)
                child_wd = add_watch(child_path, child_mask)

                if mask & IN_MASK_ADD:
                    self._masks[child_wd] |= mask
                else:
                    self._masks[child_wd] = mask

        return wd

    @override
    def remove_watch(self, path: str) -> None:
        path = normpath(abspath(path))
        remove_watch = super().remove_watch
        remove_watch(path)

        wd = self._path_to_wd.get(path)
        if wd is None:
            _logger.debug('%s: Path is not watched', path)
            return

        try:
            res = inotify_rm_watch(self._inotify_fd, wd)
            _check_return(res, path)
        finally:
            del self._path_to_wd[path]
            del self._wd_to_path[wd]
            del self._masks[wd]

        prefix = path + sep
        remove_watch_with_id = super().remove_watch_with_id
        for other_path, other_wd in list(self._path_to_wd.items()):
            if other_path.startswith(prefix):
                remove_watch_with_id(other_wd)
                self._masks.pop(other_wd, None)

    @override
    def remove_watch_with_id(self, wd: int) -> None:
        path = self._wd_to_path.get(wd)
        if path is None:
            _logger.debug('%d: Invalid handle', wd)
            return

        try:
            res = inotify_rm_watch(self._inotify_fd, wd)
            _check_return(res, path)
        finally:
            del self._wd_to_path[wd]
            del self._path_to_wd[path]
            del self._masks[wd]

        prefix = path + sep
        remove_watch_with_id = super().remove_watch_with_id
        for other_path, other_wd in list(self._path_to_wd.items()):
            if other_path.startswith(prefix):
                remove_watch_with_id(other_wd)
                self._masks.pop(other_wd, None)

    @override
    def read_event(self) -> Optional[InotifyEvent]:
        while True:
            event = super().read_event()

            if event is None:
                return None

            mask = event.mask
            watch_mask = self._masks.get(event.wd, 0)

            if mask & IN_ISDIR:
                if mask & (IN_CREATE | IN_MOVED_TO):
                    path = event.full_path()
                    self.add_watch(path, (watch_mask & ~IN_MASK_CREATE) | IN_MASK_ADD)

            if mask & IN_IGNORED:
                self._masks.pop(event.wd)

            if mask & watch_mask:
                return event

    @override
    def read_events(self, terminal_events: int = IN_Q_OVERFLOW | IN_UNMOUNT) -> list[InotifyEvent]:
        events: list[InotifyEvent] = []

        while (event := self.read_event()) is not None:
            mask = event.mask

            if mask & terminal_events:
                raise TerminalEventException(event.wd, mask, event.watch_path, event.filename)

            events.append(event)

        return events

class PollTreeNotify(TreeNotify):
    __slots__ = (
        '_epoll',
        '_stopfd',
    )

    _epoll: select.epoll
    _stopfd: Optional[int]

    def __init__(self, stopfd: Optional[int] = None) -> None:
        """
        If not `None` then `stopfd` is a file descriptor that will
        be added to the `poll()` call in `PollInotify.wait()`.

        This calls [inotify_init1(2)](https://linux.die.net/man/2/inotify_init1)
        and thus might raise an `OSError` with one of these `errno` values:
        - `EINVAL` (shouldn't happen)
        - `EMFILE`
        - `ENOMEM`
        - `ENOSYS` if your libc doesn't support [inotify_init1(2)](https://linux.die.net/man/2/inotify_init1)
        """
        super().__init__(IN_NONBLOCK | IN_CLOEXEC)
        self._stopfd = stopfd
        self._epoll = select.epoll(1 if stopfd is None else 2)
        self._epoll.register(self._inotify_fd, select.POLLIN)

        if stopfd is not None:
            self._epoll.register(stopfd, select.POLLIN)

    stopfd = PollInotify.stopfd
    close = PollInotify.close
    wait = PollInotify.wait

def main(argv: list[str]):
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument('-v', '--version',
        action='store_true',
        default=False,
        help='Print version and exit.'
    )
    ap.add_argument('-m', '--mask',
        type=_parse_mask,
        default=IN_ALL_EVENTS,
        help=f'List of flags.\n'
             f'Flags: {', '.join(flag.removeprefix('IN_') for flag in flags)}\n'
             f'[default: ALL_EVENTS]')
    ap.add_argument('path', nargs='*')

    args = ap.parse_args(argv)

    if args.version:
        print(__version__)
        return

    mask: int = args.mask
    paths: list[str] = args.path

    with TreeNotify() as tnotify:
        for filename in paths:
            tnotify.add_watch(filename, mask)

        for event in tnotify:
            print(f'{event.full_path()}: {", ".join(get_inotify_event_names(event.mask))}')

if __name__ == '__main__':
    import sys

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print()
