#!/usr/bin/env python

from panzi_inotify import Inotify, get_inotify_event_names

import sys

with Inotify() as inotify:
    for filename in sys.argv[1:]:
        inotify.add_watch(filename)

    for event in inotify:
        print(f'{event.full_path()}: {", ".join(get_inotify_event_names(event.mask))}')
