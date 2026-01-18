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

import sys

with Inotify() as inotify:
    for filename in sys.argv[1:]:
        inotify.add_watch(filename)

    while event := inotify.read_event():
        print(f'{event.watch_path}/{event.filename}: {", ".join(get_inotify_event_names(event.mask))}')
```

See [examples](examples) for more.

API Reference
-------------

### `class` `InotifyEvent`(`tuple`)

Inotify event as read from the inotify file handle.

* `cookie`: `int`
* `filename`: `Optional[str]`
* `filename_len`: `int`
* `mask`: `int`
* `watch_path`: `str`
* `wd`: `int`

#### `InotifyEvent`.`full_path`(`self`) -> `str`

Join `watch_path` and `filename`, or only `watch_path` if `filename` is `None`.



### `class` `Inotify`

Listen for inotify events.

Supports the context manager and iterator protocols.

* `_inotify_fd`: `int`
* `_inotify_stream`: `_io.BufferedReader`
* `_path_to_wd`: `dict[str, int]`
* `_wd_to_path`: `dict[int, str]`

#### `Inotify`.`__init__`(`self`, `flags`: `int` = `0x80000`) -> `None`

It's recommended to pass the `IN_CLOEXEC` flag (default).

This calls `inotify_init1()` and thus might raise an
`OSError` with one of these `errno` values:
- `EINVAL`
- `EMFILE`
- `ENOMEM`
- `ENOSYS` if your libc doesn't support `inotify_init1()`

#### `Inotify`.`add_watch`(`self`, `path`: `str`, `mask`: `int` = `0xfff`) -> `int`

Add a watch path.

This calls `inotify_add_watch()` and thus might raise one
of these exceptions:
- `PermissionError` (`EACCES`)
- `FileExistsError` (`EEXISTS`)
- `FileNotFoundError` (`ENOENT`)
- `NotADirectoryError` (`ENOTDIR`)
- `OSError` (`WBADF`, `EFAULT`, `EINVAL`, `ENAMETOOLONG`,
  `ENOMEM`, `ENOSPC`, `ENOSYS` if your libc doesn't support
  `inotify_rm_watch()`)

#### `Inotify`.`close`(`self`) -> `None`

Close the inotify handle.

Can safely be called multiple times, but you
can't call any other methods once closed.

#### `Inotify`.`closed`: `bool`

`True` if the inotify file descriptor was closed.

#### `Inotify`.`fileno`(`self`) -> `int`

The inotify file descriptor.

You can use this to call `poll()` or similar yourself
instead of using `PollInotify.wait()`.

#### `Inotify`.`get_watch_id`(`self`, `path`: `str`) -> `Optional[int]`

Get the watch id to a path, if the path is watched.

#### `Inotify`.`get_watch_path`(`self`, `wd`: `int`) -> `Optional[str]`

Get the path to a watch id, if the watch id is valid.

#### `Inotify`.`read_event`(`self`) -> `Optional[panzi_inotify.InotifyEvent]`

Read a single event. Might return `None` if there is none avaialbe.

#### `Inotify`.`read_events`(`self`, `terminal_events`: `int` = `0x6000`) -> `list[panzi_inotify.InotifyEvent]`

Read available events. Might return an empty list if there are none available.

**NOTE:** Don't use this in blocking mode! It will never return.

Raises `TerminalEventException` if the flags in `terminal_events` are set in an event `mask`.

#### `Inotify`.`remove_watch`(`self`, `path`: `str`) -> `None`

Remove watch by path.

Does nothing if the path is not watched.

This calls `inotify_rm_watch()` and this might raise an
`OSError` with one of these `errno` values:
- `EBADF`
- `EINVAL`
- `ENOSYS` if your libc doesn't support `inotify_rm_watch()`

#### `Inotify`.`remove_watch_with_id`(`self`, `wd`: `int`) -> `None`

Remove watch by handle.

Does nothing if the handle is invalid.

This calls `inotify_rm_watch()` and this might raise an
`OSError` with one of these `errno` values:
- `EBADF`
- `EINVAL`
- `ENOSYS` if your libc doesn't support `inotify_rm_watch()`

#### `Inotify`.`watch_paths`(`self`) -> `set[str]`

Get the set of the watched paths.



### `class` `PollInotify`(`panzi_inotify.Inotify`)

Listen for inotify events.

In addition to the functionality of `Inotify` this class adds a `wait()`
method that waits for events using `epoll`. If you use `Inotify` you
need/can to do that yourself.

Supports the context manager and iterator protocols.

* `_epoll`: `select.epoll`
* `_stopfd`: `Optional[int]`

#### `PollInotify`.`__init__`(`self`, `stopfd`: `Optional[int]` = `None`) -> `None`

If not `None` then `stopfd` is a file descriptor that will
be added to the `poll()` call in `PollInotify.wait()`.

This calls `inotify_init1()` and thus might raise an
`OSError` with one of these `errno` values:
- `EINVAL` (shouldn't happen)
- `EMFILE`
- `ENOMEM`
- `ENOSYS` if your libc doesn't support `inotify_init1()`

#### `PollInotify`.`close`(`self`) -> `None`

Close the inotify and epoll handles.

Can safely be called multiple times, but you
can't call any other methods once closed.

#### `PollInotify`.`stopfd`: `Optional[int]`

The `stopfd` parameter of `__init__()`, used in `wait()`.

#### `PollInotify`.`wait`(`self`, `timeout`: `Optional[float]` = `None`) -> `bool`

Wait for inotify events or for any `POLLIN` on `stopfd`,
if that is not `None`. If `stopfd` signals this function will
return `False`, otherwise `True`.

Raises `TimeoutError` if `timeout` is not `None` and
the operation has expired.

This method uses using `select.epoll.poll()`, see there for
additional possible exceptions.



### `class` `TerminalEventException`(`Exception`)

Exception raised by `Inotify.read_events()` when an event mask contains one
of the specified `terminal_events`.

* `wd`: `int`
* `mask`: `int`
* `watch_path`: `Optional[str]`
* `filename`: `Optional[str]`

#### `TerminalEventException`.`__init__`(`self`, `wd`: `int`, `mask`: `int`, `watch_path`: `Optional[str]`, `filename`: `Optional[str]`) -> `None`



### `IN_CLOEXEC`: `int`

Close inotify file descriptor on exec

### `IN_NONBLOCK`: `int`

Open inotify file descriptor as non-blocking

### `IN_ACCESS`: `int`

File was accessed.

### `IN_MODIFY`: `int`

File was modified.

### `IN_ATTRIB`: `int`

Metadata changed.

### `IN_CLOSE_WRITE`: `int`

Writtable file was closed.

### `IN_CLOSE_NOWRITE`: `int`

Unwrittable file closed.

### `IN_OPEN`: `int`

File was opened.

### `IN_MOVED_FROM`: `int`

File was moved from X.

### `IN_MOVED_TO`: `int`

File was moved to Y.

### `IN_CREATE`: `int`

Subfile was created.

### `IN_DELETE`: `int`

Subfile was deleted.

### `IN_DELETE_SELF`: `int`

Self was deleted.

### `IN_MOVE_SELF`: `int`

Self was moved.

### `IN_UNMOUNT`: `int`

Backing file system was unmounted.

### `IN_Q_OVERFLOW`: `int`

Event queued overflowed.

### `IN_IGNORED`: `int`

File was ignored.

### `IN_CLOSE`: `int`

All close events.

### `IN_MOVE`: `int`

All move events.

### `IN_ONLYDIR`: `int`

Only watch the path if it is a directory.

### `IN_DONT_FOLLOW`: `int`

Don't follow symbolic links.

### `IN_EXCL_UNLINK`: `int`

Exclude events on unlinked objects.

### `IN_MASK_CREATE`: `int`

Only create watches.

### `IN_MASK_ADD`: `int`

Add to the mask of an already existing watch.

### `IN_ISDIR`: `int`

Event occurred against dir.

### `IN_ONESHOT`: `int`

Only send event once.

### `IN_ALL_EVENTS`: `int`

All of the events.

### `get_inotify_event_names`(`mask`: `int`) -> `list[str]`

Get a list of event names from an event mask as returned by inotify.

### `INOTIFY_MASK_CODES`: `dict[int, str]`

Mapping from inotify event mask flag to it's name.

See Also
--------

[inotify(7)](https://linux.die.net/man/7/inotify)

License
-------

[Mozilla Public License Version 2.0](LICENSE.txt)
