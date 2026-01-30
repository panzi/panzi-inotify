panzi-inotify
=============

[![Test Status](https://img.shields.io/github/actions/workflow/status/panzi/panzi-inotify/tests.yml)](https://github.com/panzi/panzi-inotify/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/tag/panzi/panzi-inotify)](https://pypi.org/project/panzi_inotify/)
[![Mozilla Public License Version 2.0](https://img.shields.io/github/license/panzi/panzi-inotify)](https://github.com/panzi/panzi-inotify/blob/main/LICENSE.txt)

[API Documentation](https://panzi.github.io/panzi-inotify)

Simple inotify bindings for Python.

I didn't like all the other available inotify bindings for one reason or anther.
This one is different in these ways:

* You can import the module even if your libc doesn't support inotify. It then
  will have `HAS_INOTIFY` `False` and only if you try to create an instance of
  `Inotify` you will get an exception (`OSError(ENOSYS)`).
* It correctly handles paths that are invalid UTF-8 by using `os.fsencode()`/`os.fsdecode()`
  which use the `'surrogateescape'` Unicode error handling option. This makes
  the file paths rountrip safe.
* `wait()` and `read_events()` is separate. You can do your own wait/poll logic
  if you want.
* You can use non-blocking mode and then `read_events()` only reads the available
  events. If there are none at the moment it returns an empty array.
* You can pass a `stopfd` to `PollInotify()`. This file descriptor will be added to
  the `epoll_wait()` call in `PollInotify.wait()`. If `POLLIN` signals for that
  then `wait()` will return `False`. This is meant for implementing a way to stop
  a thread that waits for events without a timeout.
* Translates errors to the appropriate Python exceptions from the given `errno`
  (`FileNotFoundError`, `PermissionError` etc. and `OSError` as fallback).
* Uses Mozilla Public License Version 2.0, so you can use it from proprietary
  code, yet it isn't as permissive as MIT or BSD.

Installation
------------

Via pip:

```bash
$ pip install panzi-inotify
```

Form source:

```bash
$ git clone git@github.com:panzi/panzi-inotify.git
$ pip install ./panzi-inotify
```

Example
-------

```Python
from panzi_inotify import Inotify, get_inotify_event_names

import sys

with Inotify() as inotify:
    for filename in sys.argv[1:]:
        inotify.add_watch(filename)

    for event in inotify:
        print(f'{event.full_path()}: {", ".join(get_inotify_event_names(event.mask))}')
```

See [examples](https://github.com/panzi/panzi-inotify/tree/main/examples) for more.

You can also run a basic command line too to listen for events on a set of paths
like this:

```bash
python -m panzi_inotify [--mask=MASK] <path>...
```

For more on this see:

```bash
python -m panzi_inotify --help
```

See Also
--------

[inotify(7)](https://linux.die.net/man/7/inotify)
