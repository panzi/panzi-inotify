#!/usr/bin/env python

from panzi_inotify import Inotify, get_inotify_event_names

import sys

with Inotify() as inotify:
    for filename in sys.argv[1:]:
        inotify.add_watch(filename)

    while event := inotify.read_event():
        print(f'{event.watch_path}/{event.filename}: {", ".join(get_inotify_event_names(event.mask))}')
