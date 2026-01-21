import os
import pytest

from os.path import join as join_path
from panzi_inotify import *
from testutils import *

# These are only some basic tests for the `Inotify` class.
# TODO: Also test `PollInotify` including `terminal_events`.

def test_watch_file(watch_file: str, subtests: pytest.Subtests) -> None:
    with Inotify(IN_CLOEXEC | IN_NONBLOCK) as inotify:
        wd = inotify.add_watch(watch_file)

        with subtests.test('write to file'):
            write_file(watch_file, 'change')

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_OPEN, 'watch_path': watch_file, 'filename': None },
                { 'wd': wd, 'mask': IN_MODIFY, 'watch_path': watch_file, 'filename': None },
                { 'wd': wd, 'mask': IN_CLOSE_WRITE, 'watch_path': watch_file, 'filename': None },
            ])

        with subtests.test('change attributes'):
            os.chmod(watch_file, 0o766)

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_ATTRIB, 'watch_path': watch_file, 'filename': None },
            ])

        with subtests.test('rename watched file'):
            os.rename(watch_file, f'{watch_file}_moved')

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_MOVE_SELF, 'watch_path': watch_file, 'filename': None },
            ])

        with subtests.test('delete file'):
            os.unlink(f'{watch_file}_moved')

            event = inotify.read_event() # also test read_event() method
            assert_events([event] if event is not None else [], [
                { 'wd': wd, 'mask': IN_ATTRIB, 'watch_path': watch_file, 'filename': None },
            ])

            event = inotify.read_event() # also test read_event() method
            assert_events([event] if event is not None else [], [
                { 'wd': wd, 'mask': IN_DELETE_SELF, 'watch_path': watch_file, 'filename': None },
            ])

            event = inotify.read_event() # also test read_event() method
            assert_events([event] if event is not None else [], [
                { 'wd': wd, 'mask': IN_IGNORED, 'watch_path': watch_file, 'filename': None },
            ])

            assert inotify.watch_paths() == set()

            assert_events(inotify.read_events(), [])

def test_watch_dir(watch_dir: str, subtests: pytest.Subtests) -> None:
    with Inotify(IN_CLOEXEC | IN_NONBLOCK) as inotify:
        wd = inotify.add_watch(watch_dir)

        with subtests.test('create file'):
            write_file(join_path(watch_dir, 'a.txt'))

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_CREATE, 'watch_path': watch_dir, 'filename': 'a.txt' },
                { 'wd': wd, 'mask': IN_OPEN, 'watch_path': watch_dir, 'filename': 'a.txt' },
                { 'wd': wd, 'mask': IN_CLOSE_WRITE, 'watch_path': watch_dir, 'filename': 'a.txt' },
            ])

        with subtests.test('create sub-directory'):
            os.mkdir(join_path(watch_dir, 'subdir'))

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_CREATE | IN_ISDIR, 'watch_path': watch_dir, 'filename': 'subdir' },
            ])

        with subtests.test('rename file'):
            os.rename(
                join_path(watch_dir, 'a.txt'),
                join_path(watch_dir, 'b.txt'),
            )

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_MOVED_FROM, 'watch_path': watch_dir, 'filename': 'a.txt' },
                { 'wd': wd, 'mask': IN_MOVED_TO, 'watch_path': watch_dir, 'filename': 'b.txt' },
            ])

        with subtests.test('write to file'):
            write_file(join_path(watch_dir, 'b.txt'), 'change')

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_OPEN, 'watch_path': watch_dir, 'filename': 'b.txt' },
                { 'wd': wd, 'mask': IN_MODIFY, 'watch_path': watch_dir, 'filename': 'b.txt' },
                { 'wd': wd, 'mask': IN_CLOSE_WRITE, 'watch_path': watch_dir, 'filename': 'b.txt' },
            ])

        with subtests.test('read file'):
            read_file(join_path(watch_dir, 'b.txt'))

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_OPEN, 'watch_path': watch_dir, 'filename': 'b.txt' },
                { 'wd': wd, 'mask': IN_ACCESS, 'watch_path': watch_dir, 'filename': 'b.txt' },
                { 'wd': wd, 'mask': IN_CLOSE_NOWRITE, 'watch_path': watch_dir, 'filename': 'b.txt' },
            ])

        with subtests.test('change attributes'):
            os.chmod(join_path(watch_dir, 'b.txt'), 0o766)

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_ATTRIB, 'watch_path': watch_dir, 'filename': 'b.txt' },
            ])

        with subtests.test('delete file'):
            os.unlink(join_path(watch_dir, 'b.txt'))

            event = inotify.read_event() # also test read_event() method
            assert_events([event] if event is not None else [], [
                { 'wd': wd, 'mask': IN_DELETE, 'watch_path': watch_dir, 'filename': 'b.txt' },
            ])

        with subtests.test('rename watched directory'):
            os.rename(watch_dir, f'{watch_dir}_moved')

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_MOVE_SELF, 'watch_path': watch_dir, 'filename': None },
            ])

        with subtests.test('delete watched directory'):
            os.rmdir(join_path(f'{watch_dir}_moved', 'subdir'))
            os.rmdir(f'{watch_dir}_moved')

            assert_events(inotify.read_events(), [
                { 'wd': wd, 'mask': IN_DELETE | IN_ISDIR, 'watch_path': watch_dir, 'filename': 'subdir' },
                { 'wd': wd, 'mask': IN_DELETE_SELF, 'watch_path': watch_dir, 'filename': None },
                { 'wd': wd, 'mask': IN_IGNORED, 'watch_path': watch_dir, 'filename': None },
            ])

            assert inotify.watch_paths() == set()

            assert_events(inotify.read_events(), [])
