# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re
import sys
import argparse

import panzi_inotify
from . import Inotify, get_inotify_event_names, IN_ALL_EVENTS, __version__

flags = [
    'IN_ACCESS',
    'IN_MODIFY',
    'IN_ATTRIB',
    'IN_CLOSE_WRITE',
    'IN_CLOSE_NOWRITE',
    'IN_OPEN',
    'IN_MOVED_FROM',
    'IN_MOVED_TO',
    'IN_CREATE',
    'IN_DELETE',
    'IN_DELETE_SELF',
    'IN_MOVE_SELF',
    'IN_ONLYDIR',
    'IN_DONT_FOLLOW',
    'IN_EXCL_UNLINK',
    'IN_MASK_CREATE',
    'IN_MASK_ADD',
    'IN_ONESHOT',
    'IN_ALL_EVENTS',
]

flag_dict = {
    name.removeprefix('IN_'): getattr(panzi_inotify, name)
    for name in flags
}

SEP = re.compile(r'[+|,\s]')

def _parse_mask(value: str) -> int:
    mask = 0
    value = value.strip()
    if value:
        for item in SEP.split(value):
            item = item.strip()
            uitem = item.upper().replace('-', '_')
            flag = flag_dict.get(uitem)

            if flag is None:
                flag = flag_dict.get(uitem.removeprefix('IN_'))

            if flag is None:
                try:
                    flag = int(uitem, 0)
                except ValueError as exc:
                    try:
                        # for 0-padded decimal numbers
                        flag = int(uitem, 10)
                    except:
                        raise ValueError(f'illegal flag name: {item}') from exc

            mask |= flag
    return mask

_parse_mask.__name__ = 'event mask'

def main(argv: list[str]):
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
             f'Flags: {', '.join(flag_dict)}\n'
             f'[default: ALL_EVENTS]')
    ap.add_argument('path', nargs='*')

    args = ap.parse_args(argv)

    if args.version:
        print(__version__)
        return

    mask: int = args.mask
    paths: list[str] = args.path

    with Inotify() as inotify:
        for filename in paths:
            inotify.add_watch(filename, mask)

        for event in inotify:
            print(f'{event.full_path()}: {", ".join(get_inotify_event_names(event.mask))}')

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print()
