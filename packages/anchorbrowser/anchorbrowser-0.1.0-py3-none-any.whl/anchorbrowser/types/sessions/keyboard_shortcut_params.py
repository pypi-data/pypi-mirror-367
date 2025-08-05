# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["KeyboardShortcutParams"]


class KeyboardShortcutParams(TypedDict, total=False):
    keys: Required[List[str]]
    """Array of keys to press simultaneously"""

    hold_time: Annotated[int, PropertyInfo(alias="holdTime")]
    """Time to hold the keys down in milliseconds"""
