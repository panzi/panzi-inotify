
from typing import Generator

import os
import sys
import shutil
import pytest

from pathlib import Path
from os.path import join as join_path
from tempfile import gettempdir

SRC_PATH = str(Path(__file__).resolve().parent.parent)

if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

@pytest.fixture(scope="function")
def temp_prefix(request: pytest.FixtureRequest) -> tuple[str, str]:
    tempdir = gettempdir()
    PID = os.getpid()
    func_name = request.function.__name__

    return tempdir, f'logmon.test.{PID}.{func_name}'

@pytest.fixture(scope="function")
def watch_dir(temp_prefix: tuple[str, str]) -> Generator[str, None, None]:
    tempdir, prefix = temp_prefix
    path = join_path(tempdir, prefix)
    os.mkdir(path)
    try:
        yield path
    finally:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass

@pytest.fixture(scope="function")
def watch_file(temp_prefix: tuple[str, str]) -> Generator[str, None, None]:
    tempdir, prefix = temp_prefix
    path = join_path(tempdir, f"{prefix}.txt")

    with open(path, 'w'):
        pass

    try:
        yield path
    finally:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
