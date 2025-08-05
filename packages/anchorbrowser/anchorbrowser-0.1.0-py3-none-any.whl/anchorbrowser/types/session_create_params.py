# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = [
    "SessionCreateParams",
    "Browser",
    "BrowserAdblock",
    "BrowserCaptchaSolver",
    "BrowserHeadless",
    "BrowserP2pDownload",
    "BrowserPopupBlocker",
    "BrowserProfile",
    "BrowserViewport",
    "Session",
    "SessionLiveView",
    "SessionProxy",
    "SessionProxyAnchorResidentialProxyType",
    "SessionProxyAnchorMobileProxyType",
    "SessionProxyCustomProxyType",
    "SessionRecording",
    "SessionTimeout",
]


class SessionCreateParams(TypedDict, total=False):
    browser: Browser
    """Browser-specific configurations."""

    session: Session
    """Session-related configurations."""


class BrowserAdblock(TypedDict, total=False):
    active: bool
    """Enable or disable ad-blocking. Defaults to `true`."""


class BrowserCaptchaSolver(TypedDict, total=False):
    active: bool
    """Enable or disable captcha-solving.

    Requires proxy to be active. Defaults to `false`.
    """


class BrowserHeadless(TypedDict, total=False):
    active: bool
    """Whether browser should be headless or headful. Defaults to `false`."""


class BrowserP2pDownload(TypedDict, total=False):
    active: bool
    """Enable or disable P2P downloads.

    When enabled, the browser will capture downloads for direct data extraction,
    instead of uploading them on Anchor's storage. Defaults to `false`.
    """


class BrowserPopupBlocker(TypedDict, total=False):
    active: bool
    """Blocks popups, including ads and CAPTCHA consent banners.

    Requires adblock to be active. Defaults to `true`.
    """


class BrowserProfile(TypedDict, total=False):
    name: str
    """The name of the profile to be used during the browser session."""

    persist: bool
    """
    Indicates whether the browser session profile data should be saved when the
    browser session ends. Defaults to `false`.
    """

    store_cache: bool
    """
    Indicates whether the browser session cache should be saved when the browser
    session ends. Defaults to `false`.
    """


class BrowserViewport(TypedDict, total=False):
    height: int
    """Height of the viewport in pixels. Defaults to `900`."""

    width: int
    """Width of the viewport in pixels. Defaults to `1440`."""


class Browser(TypedDict, total=False):
    adblock: BrowserAdblock
    """Configuration for ad-blocking."""

    captcha_solver: BrowserCaptchaSolver
    """Configuration for captcha-solving."""

    headless: BrowserHeadless
    """Configuration for headless mode."""

    p2p_download: BrowserP2pDownload
    """Configuration for peer-to-peer download capture functionality."""

    popup_blocker: BrowserPopupBlocker
    """Configuration for popup blocking."""

    profile: BrowserProfile
    """Options for managing and persisting browser session profiles."""

    viewport: BrowserViewport
    """Configuration for the browser's viewport size."""


class SessionLiveView(TypedDict, total=False):
    read_only: bool
    """Enable or disable read-only mode for live viewing. Defaults to `false`."""


class SessionProxyAnchorResidentialProxyType(TypedDict, total=False):
    type: Required[Literal["anchor_residential"]]

    active: bool
    """Enable or disable proxy usage. Defaults to `false`."""

    country_code: Literal["us", "uk", "fr", "it", "jp", "au", "de", "fi", "ca"]
    """Country code for residential proxy"""


class SessionProxyAnchorMobileProxyType(TypedDict, total=False):
    type: Required[Literal["anchor_mobile"]]

    active: bool
    """Enable or disable proxy usage. Defaults to `false`."""

    country_code: Literal["us", "uk", "fr", "it", "jp", "au", "de", "fi", "ca"]
    """Country code for mobile proxy"""


class SessionProxyCustomProxyType(TypedDict, total=False):
    password: Required[str]
    """Proxy password"""

    server: Required[str]
    """Proxy server address"""

    type: Required[Literal["custom"]]

    username: Required[str]
    """Proxy username"""

    active: bool
    """Enable or disable proxy usage. Defaults to `false`."""


SessionProxy: TypeAlias = Union[
    SessionProxyAnchorResidentialProxyType, SessionProxyAnchorMobileProxyType, SessionProxyCustomProxyType
]


class SessionRecording(TypedDict, total=False):
    active: bool
    """Enable or disable video recording of the browser session. Defaults to `true`."""


class SessionTimeout(TypedDict, total=False):
    idle_timeout: int
    """
    The amount of time (in minutes) the browser session waits for new connections
    after all others are closed before stopping. Defaults to `5`.
    """

    max_duration: int
    """Maximum amount of time (in minutes) for the browser to run before terminating.

    Defaults to `20`.
    """


class Session(TypedDict, total=False):
    live_view: SessionLiveView
    """Configuration for live viewing the browser session."""

    proxy: SessionProxy
    """Configuration options for proxy usage."""

    recording: SessionRecording
    """Configuration for session recording."""

    timeout: SessionTimeout
    """Timeout configurations for the browser session."""
