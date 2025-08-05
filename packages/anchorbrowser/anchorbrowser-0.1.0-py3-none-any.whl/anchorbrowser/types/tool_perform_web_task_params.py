# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ToolPerformWebTaskParams"]


class ToolPerformWebTaskParams(TypedDict, total=False):
    prompt: Required[str]
    """The task to be autonomously completed."""

    session_id: Annotated[str, PropertyInfo(alias="sessionId")]
    """
    An optional browser session identifier to reference an existing running browser
    sessions. When passed, the tool will be executed on the provided browser
    session.
    """

    output_schema: object
    """JSON Schema defining the expected structure of the output data."""

    url: str
    """The URL of the webpage.

    If not provided, the tool will use the current page in the session.
    """
