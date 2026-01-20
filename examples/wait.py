#!/usr/bin/env python

from panzi_inotify import PollInotify, get_inotify_event_names

import os
import sys
import signal

stopfd_read, stopfd_write = os.pipe()

def handle_signal(sig: int, frame) -> None:
    # could also happen in another thread
    print("shutdown...")
    os.write(stopfd_write, b'\0')

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# For long running processes that do multiple things at once, including but not
# limited to multi-threading, you can use `PollInotify` which provides a
# `wait()` method and the option to wait on an additional file descriptor to
# detect when it should stop.
with PollInotify(stopfd_read) as inotify:
    for filename in sys.argv[1:]:
        inotify.add_watch(filename)

    while inotify.wait():
        for event in inotify.read_events():
            print(f'{event.full_path()}: {", ".join(get_inotify_event_names(event.mask))}')

os.close(stopfd_read)
os.close(stopfd_write)
