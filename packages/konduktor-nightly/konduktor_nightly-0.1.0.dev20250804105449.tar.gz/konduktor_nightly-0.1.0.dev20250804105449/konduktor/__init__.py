"""The Konduktor package."""

import os
import subprocess

from konduktor.execution import launch
from konduktor.resource import Resources
from konduktor.task import Task

__all__ = [
    'launch',
    'Resources',
    'Task',
]

# Replaced with the current commit when building the wheels.
_KONDUKTOR_COMMIT_SHA = '546df0fd04cca8e7f30b4ef5f86ee1043663534b'
os.makedirs(os.path.expanduser('~/.konduktor'), exist_ok=True)


def _get_git_commit():
    if 'KONDUKTOR_COMMIT_SHA' not in _KONDUKTOR_COMMIT_SHA:
        # This is a release build, so we don't need to get the commit hash from
        # git, as it's already been set.
        return _KONDUKTOR_COMMIT_SHA

    # This is a development build (pip install -e .), so we need to get the
    # commit hash from git.
    try:
        cwd = os.path.dirname(__file__)
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=cwd,
            universal_newlines=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        changes = subprocess.check_output(
            ['git', 'status', '--porcelain'],
            cwd=cwd,
            universal_newlines=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if changes:
            commit_hash += '-dirty'
        return commit_hash
    except Exception:  # pylint: disable=broad-except
        return _KONDUKTOR_COMMIT_SHA


__commit__ = _get_git_commit()
__version__ = '1.0.0.dev0.1.0.dev20250804105449'
__root_dir__ = os.path.dirname(os.path.abspath(__file__))
