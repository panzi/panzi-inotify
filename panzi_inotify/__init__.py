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
from .inotify import __all__

__version__ = '1.0.0'
