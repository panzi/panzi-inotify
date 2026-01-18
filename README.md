panzi-inotify
=============

Simple inotify bindings for Python.

I didn't like all the other available inotify bindings for one reason or anther.
This one is different in these ways:

* You can import the module even if your libc doesn't support inotify. It then
  will have `HAS_INOTIFY` `false` and only if you try to create an instance of
  `Inotify` you will get an exception (`OSError(ENOSYS)`).
* It correctly handles paths that are invalid UTF-8 by using the `'surrogateescape'`
  escape Unicode error handling option. This makes the file paths rountrip safe.
* `wait()` and `read_events()` is separate. You can do your own wait/poll logic
  if you want.
* `read_events()` only reads the available events. If there are none at the moment
  it returns an empty array.
* You can pass a `stopfd` to `Inotify()`. This file descriptor will be added to
  `epoll_wait()` call in `Inotify.wait()`. If `POLLIN` signals for that `wait()`
  will return `False`. This is meant for implementing a way to stop a process that
  waits for events without a timeout.
* Translates errors in the approprioate Python exceptions from the given
  `errno` (`FileNotFoundError` etc. and `OSError` as fallback).

Example
-------

```Python
from panzi_inotify import Inotify, get_inotify_event_names

import os
import sys
import signal

stopfd_read, stopfd_write = os.pipe()

def handle_signal(sig: int, frame):
    print("shutdown...")
    os.write(stopfd_write, b'\0')

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

with Inotify(stopfd_read) as inotify:
    for filename in sys.argv[1:]:
        inotify.add_watch(filename)

    while inotify.wait():
        for event in inotify.read_events():
            print(f'{event.watch_path}/{event.filename}: {", ".join(get_inotify_event_names(event.mask))}')

os.close(stopfd_read)
os.close(stopfd_write)
```

See Also
--------

[inotify(7)](https://linux.die.net/man/7/inotify)
