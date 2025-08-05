# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ProfileCreateParams"]


class ProfileCreateParams(TypedDict, total=False):
    name: Required[str]
    """The name of the profile."""

    description: str
    """A description of the profile."""

    session_id: str
    """The browser session ID is required if the source is set to `session`.

    The browser session must be running, and the profile will be stored once the
    browser session terminates.
    """

    source: Literal["session"]
    """The source of the profile data. currently only `session` is supported."""

    store_cache: bool
    """
    Indicates whether the browser session cache should be saved when the browser
    session ends. Defaults to `false`.
    """
