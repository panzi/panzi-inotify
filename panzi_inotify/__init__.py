# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
**Source: [GitHub](https://github.com/panzi/panzi-inotify/)**

### Example

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

### See Also

[inotify(7)](https://linux.die.net/man/7/inotify)
"""

from .inotify import *
from .inotify import __version__
from .treenotify import *

__all__ = (
    'InotifyEvent',
    'Inotify',
    'PollInotify',
    'TreeNotify',
    'PollTreeNotify',
    'TerminalEventException',
    'get_inotify_event_names',
    'IN_CLOEXEC',
    'IN_NONBLOCK',
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
    'IN_UNMOUNT',
    'IN_Q_OVERFLOW',
    'IN_IGNORED',
    'IN_CLOSE',
    'IN_MOVE',
    'IN_ONLYDIR',
    'IN_DONT_FOLLOW',
    'IN_EXCL_UNLINK',
    'IN_MASK_CREATE',
    'IN_MASK_ADD',
    'IN_ISDIR',
    'IN_ONESHOT',
    'IN_ALL_EVENTS',
    'INOTIFY_MASK_CODES',
)
