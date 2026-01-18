#!/usr/bin/env python

from panzi_inotify import PollInotify, get_inotify_event_names

import os
import sys
import signal

stopfd_read, stopfd_write = os.pipe()

def handle_signal(sig: int, frame):
    # could also happen in another thread
    print("shutdown...")
    os.write(stopfd_write, b'\0')

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

with PollInotify(stopfd_read) as inotify:
    for filename in sys.argv[1:]:
        inotify.add_watch(filename)

    while inotify.wait():
        for event in inotify.read_events():
            print(f'{event.watch_path}/{event.filename}: {", ".join(get_inotify_event_names(event.mask))}')

os.close(stopfd_read)
os.close(stopfd_write)
