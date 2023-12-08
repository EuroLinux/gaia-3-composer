"""
Composer types for mypy.
"""

import typing as t


class CommandsDataType(t.TypedDict, total=True):
    mkdir: list[str]
    mv: list[tuple[str, str]]
    ln: list[tuple[str, str]]
