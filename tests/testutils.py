from os.path import join as join_path
from typing import TypedDict, NotRequired, Optional
from itertools import zip_longest
from panzi_inotify import InotifyEvent, get_inotify_event_names

__all__ = (
    'write_file',
    'read_file',
    'assert_events',
)

def write_file(path: str, data: str='') -> None:
    with open(path, 'w') as fp:
        fp.write(data)

def read_file(path: str) -> str:
    with open(path, 'r') as fp:
        return fp.read()

class EventTestData(TypedDict):
    wd: NotRequired[int]
    mask: NotRequired[int]
    cookie: NotRequired[int]
    filename_len: NotRequired[int]
    watch_path: NotRequired[str]
    filename: NotRequired[Optional[str]]

def assert_events(actual: list[InotifyEvent], expected: list[EventTestData], message: str|None=None) -> None:
    actual_dicts = [
        { key: getattr(actual_event, key) for key in expected_event }
        for actual_event, expected_event in zip_longest(actual, expected, fillvalue=())
    ]

    if message is not None:
        assert actual_dicts == expected, message
    else:
        assert actual_dicts == expected, f'''\
Events missmatch.

    Actual ({len(actual)}):
        {'\n        '.join(
            f"{a.full_path()}: wd: {a.wd}, cookie: {a.cookie}, mask: [{", ".join(get_inotify_event_names(a.mask))}]"
            for a in actual
        )}

    Expected ({len(expected)}):
        {'\n        '.join(
            format_expected_event(e) for e in expected
        )}
'''

def format_expected_event(event: EventTestData) -> str:
    buf: list[str] = []
    wd = event.get('wd')
    mask = event.get('mask')
    cookie = event.get('cookie')
    watch_path = event.get('watch_path')
    filename = event.get('filename')

    if watch_path is not None and filename is not None:
        buf.append(join_path(watch_path, filename))
        buf.append(': ')

    elif watch_path is not None:
        buf.append(watch_path)
        buf.append(': ')

    elif filename:
        buf.append(join_path('*', filename))
        buf.append(': ')

    else:
        buf.append('*: ')

    buf.append(f'wd: {wd}' if wd is not None else 'wd: *')
    buf.append(f', cookie: {cookie}' if cookie is not None else ', cookie: *')
    buf.append(f', mask: [{", ".join(get_inotify_event_names(mask))}]' if mask is not None else ', mask: *')

    return ''.join(buf)
