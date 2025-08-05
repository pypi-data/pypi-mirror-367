# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import tool_fetch_webpage_params, tool_perform_web_task_params, tool_screenshot_webpage_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.tool_perform_web_task_response import ToolPerformWebTaskResponse

__all__ = ["ToolsResource", "AsyncToolsResource"]


class ToolsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ToolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return ToolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ToolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return ToolsResourceWithStreamingResponse(self)

    def fetch_webpage(
        self,
        *,
        session_id: str | NotGiven = NOT_GIVEN,
        format: Literal["html", "markdown"] | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Retrieve the rendered content of a webpage, optionally formatted as Markdown or
        HTML.

        Args:
          session_id: An optional browser session identifier to reference an existing running browser
              session. If provided, the tool will execute within that browser session.

          format: The output format of the content.

          url: The URL of the webpage to fetch content from. When left empty, the current
              webpage is used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return self._post(
            "/v1/tools/fetch-webpage",
            body=maybe_transform(
                {
                    "format": format,
                    "url": url,
                },
                tool_fetch_webpage_params.ToolFetchWebpageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"session_id": session_id}, tool_fetch_webpage_params.ToolFetchWebpageParams),
            ),
            cast_to=str,
        )

    def perform_web_task(
        self,
        *,
        prompt: str,
        session_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ToolPerformWebTaskResponse:
        """
        Start from a URL and perform the given task.

        Args:
          prompt: The task to be autonomously completed.

          session_id: An optional browser session identifier to reference an existing running browser
              sessions. When passed, the tool will be executed on the provided browser
              session.

          output_schema: JSON Schema defining the expected structure of the output data.

          url: The URL of the webpage. If not provided, the tool will use the current page in
              the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/tools/perform-web-task",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "output_schema": output_schema,
                    "url": url,
                },
                tool_perform_web_task_params.ToolPerformWebTaskParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"session_id": session_id}, tool_perform_web_task_params.ToolPerformWebTaskParams
                ),
            ),
            cast_to=ToolPerformWebTaskResponse,
        )

    def screenshot_webpage(
        self,
        *,
        session_id: str | NotGiven = NOT_GIVEN,
        capture_full_height: bool | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        image_quality: int | NotGiven = NOT_GIVEN,
        s3_target_address: str | NotGiven = NOT_GIVEN,
        scroll_all_content: bool | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        wait: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        This endpoint captures a screenshot of the specified webpage using Chromium.
        Users can customize the viewport dimensions and capture options.

        Args:
          session_id: An optional browser session identifier to reference an existing running browser
              sessions. When passed, the tool will be executed on the provided browser
              session.

          capture_full_height: If true, captures the entire height of the page, ignoring the viewport height.

          height: The height of the browser viewport in pixels.

          image_quality: Quality of the output image, on the range 1-100. 100 will not perform any
              compression.

          s3_target_address: Presigned S3 url target to upload the image to.

          scroll_all_content: If true, scrolls the page and captures all visible content.

          url: The URL of the webpage to capture.

          wait: Duration in milliseconds to wait after page has loaded, mainly used for sites
              with JS animations.

          width: The width of the browser viewport in pixels.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        return self._post(
            "/v1/tools/screenshot",
            body=maybe_transform(
                {
                    "capture_full_height": capture_full_height,
                    "height": height,
                    "image_quality": image_quality,
                    "s3_target_address": s3_target_address,
                    "scroll_all_content": scroll_all_content,
                    "url": url,
                    "wait": wait,
                    "width": width,
                },
                tool_screenshot_webpage_params.ToolScreenshotWebpageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"session_id": session_id}, tool_screenshot_webpage_params.ToolScreenshotWebpageParams
                ),
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncToolsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncToolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#accessing-raw-response-data-eg-headers
        """
        return AsyncToolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncToolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/anchorbrowser/AnchorBrowser-SDK-Python#with_streaming_response
        """
        return AsyncToolsResourceWithStreamingResponse(self)

    async def fetch_webpage(
        self,
        *,
        session_id: str | NotGiven = NOT_GIVEN,
        format: Literal["html", "markdown"] | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Retrieve the rendered content of a webpage, optionally formatted as Markdown or
        HTML.

        Args:
          session_id: An optional browser session identifier to reference an existing running browser
              session. If provided, the tool will execute within that browser session.

          format: The output format of the content.

          url: The URL of the webpage to fetch content from. When left empty, the current
              webpage is used.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return await self._post(
            "/v1/tools/fetch-webpage",
            body=await async_maybe_transform(
                {
                    "format": format,
                    "url": url,
                },
                tool_fetch_webpage_params.ToolFetchWebpageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"session_id": session_id}, tool_fetch_webpage_params.ToolFetchWebpageParams
                ),
            ),
            cast_to=str,
        )

    async def perform_web_task(
        self,
        *,
        prompt: str,
        session_id: str | NotGiven = NOT_GIVEN,
        output_schema: object | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ToolPerformWebTaskResponse:
        """
        Start from a URL and perform the given task.

        Args:
          prompt: The task to be autonomously completed.

          session_id: An optional browser session identifier to reference an existing running browser
              sessions. When passed, the tool will be executed on the provided browser
              session.

          output_schema: JSON Schema defining the expected structure of the output data.

          url: The URL of the webpage. If not provided, the tool will use the current page in
              the session.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/tools/perform-web-task",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "output_schema": output_schema,
                    "url": url,
                },
                tool_perform_web_task_params.ToolPerformWebTaskParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"session_id": session_id}, tool_perform_web_task_params.ToolPerformWebTaskParams
                ),
            ),
            cast_to=ToolPerformWebTaskResponse,
        )

    async def screenshot_webpage(
        self,
        *,
        session_id: str | NotGiven = NOT_GIVEN,
        capture_full_height: bool | NotGiven = NOT_GIVEN,
        height: int | NotGiven = NOT_GIVEN,
        image_quality: int | NotGiven = NOT_GIVEN,
        s3_target_address: str | NotGiven = NOT_GIVEN,
        scroll_all_content: bool | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        wait: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        This endpoint captures a screenshot of the specified webpage using Chromium.
        Users can customize the viewport dimensions and capture options.

        Args:
          session_id: An optional browser session identifier to reference an existing running browser
              sessions. When passed, the tool will be executed on the provided browser
              session.

          capture_full_height: If true, captures the entire height of the page, ignoring the viewport height.

          height: The height of the browser viewport in pixels.

          image_quality: Quality of the output image, on the range 1-100. 100 will not perform any
              compression.

          s3_target_address: Presigned S3 url target to upload the image to.

          scroll_all_content: If true, scrolls the page and captures all visible content.

          url: The URL of the webpage to capture.

          wait: Duration in milliseconds to wait after page has loaded, mainly used for sites
              with JS animations.

          width: The width of the browser viewport in pixels.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        return await self._post(
            "/v1/tools/screenshot",
            body=await async_maybe_transform(
                {
                    "capture_full_height": capture_full_height,
                    "height": height,
                    "image_quality": image_quality,
                    "s3_target_address": s3_target_address,
                    "scroll_all_content": scroll_all_content,
                    "url": url,
                    "wait": wait,
                    "width": width,
                },
                tool_screenshot_webpage_params.ToolScreenshotWebpageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"session_id": session_id}, tool_screenshot_webpage_params.ToolScreenshotWebpageParams
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class ToolsResourceWithRawResponse:
    def __init__(self, tools: ToolsResource) -> None:
        self._tools = tools

        self.fetch_webpage = to_raw_response_wrapper(
            tools.fetch_webpage,
        )
        self.perform_web_task = to_raw_response_wrapper(
            tools.perform_web_task,
        )
        self.screenshot_webpage = to_custom_raw_response_wrapper(
            tools.screenshot_webpage,
            BinaryAPIResponse,
        )


class AsyncToolsResourceWithRawResponse:
    def __init__(self, tools: AsyncToolsResource) -> None:
        self._tools = tools

        self.fetch_webpage = async_to_raw_response_wrapper(
            tools.fetch_webpage,
        )
        self.perform_web_task = async_to_raw_response_wrapper(
            tools.perform_web_task,
        )
        self.screenshot_webpage = async_to_custom_raw_response_wrapper(
            tools.screenshot_webpage,
            AsyncBinaryAPIResponse,
        )


class ToolsResourceWithStreamingResponse:
    def __init__(self, tools: ToolsResource) -> None:
        self._tools = tools

        self.fetch_webpage = to_streamed_response_wrapper(
            tools.fetch_webpage,
        )
        self.perform_web_task = to_streamed_response_wrapper(
            tools.perform_web_task,
        )
        self.screenshot_webpage = to_custom_streamed_response_wrapper(
            tools.screenshot_webpage,
            StreamedBinaryAPIResponse,
        )


class AsyncToolsResourceWithStreamingResponse:
    def __init__(self, tools: AsyncToolsResource) -> None:
        self._tools = tools

        self.fetch_webpage = async_to_streamed_response_wrapper(
            tools.fetch_webpage,
        )
        self.perform_web_task = async_to_streamed_response_wrapper(
            tools.perform_web_task,
        )
        self.screenshot_webpage = async_to_custom_streamed_response_wrapper(
            tools.screenshot_webpage,
            AsyncStreamedBinaryAPIResponse,
        )
