import sys

from . import Inotify, get_inotify_event_names, logging, _logger

def main():
    _logger.setLevel(logging.DEBUG)

    with Inotify() as inotify:
        for filename in sys.argv[1:]:
            inotify.add_watch(filename)

        for event in inotify:
            print(f'{event.full_path()}: {", ".join(get_inotify_event_names(event.mask))}')

if __name__ == '__main__':
    main()
