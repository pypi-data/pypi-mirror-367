# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from .parse import (
    ParseResource,
    AsyncParseResource,
    ParseResourceWithRawResponse,
    AsyncParseResourceWithRawResponse,
    ParseResourceWithStreamingResponse,
    AsyncParseResourceWithStreamingResponse,
)
from ...types import task_get_params, task_list_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncTasksPage, AsyncTasksPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.task.task import Task

__all__ = ["TaskResource", "AsyncTaskResource"]


class TaskResource(SyncAPIResource):
    @cached_property
    def parse(self) -> ParseResource:
        return ParseResource(self._client)

    @cached_property
    def with_raw_response(self) -> TaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return TaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return TaskResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        cursor: Union[str, datetime] | NotGiven = NOT_GIVEN,
        end: Union[str, datetime] | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        start: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncTasksPage[Task]:
        """Retrieves a list of tasks with cursor-based pagination.

        By default, tasks are
        returned in descending order (newest first).

        ## Default Behaviors:

        - **limit**: Returns all tasks if not specified
        - **start**: No start date filter (returns from beginning of time)
        - **end**: No end date filter (returns up to current time)
        - **cursor**: Starts from most recent tasks (no pagination offset)
        - **sort**: 'desc' (descending order, newest first)
        - **include_chunks**: false (excludes chunks for better performance)
        - **base64_urls**: false (returns presigned URLs instead of base64)

        ## Common Usage Patterns:

        **Basic usage (get all tasks):** `GET /api/v1/tasks`

        **Get first 10 tasks:** `GET /api/v1/tasks?limit=10`

        **Paginate through results:**

        1. First request: `GET /api/v1/tasks?limit=10`
        2. Use next_cursor from response for subsequent pages:
           `GET /api/v1/tasks?limit=10&cursor=<timestamp>`

        **Filter by date range:**
        `GET /api/v1/tasks?start=2025-01-01T00:00:00Z&end=2025-12-31T23:59:59Z`

        **Get detailed results with chunks:** `GET /api/v1/tasks?include_chunks=true`

        **Get base64 encoded content:** `GET /api/v1/tasks?base64_urls=true`

        **Get tasks in ascending order (oldest first):** `GET /api/v1/tasks?sort=asc`

        **Get tasks in descending order (newest first, default):**
        `GET /api/v1/tasks?sort=desc`

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          cursor: Cursor for pagination (timestamp)

          end: End date

          include_chunks: Whether to include chunks in the output response

          limit: Number of tasks per page

          sort: Sort order: 'asc' for ascending, 'desc' for descending (default)

          start: Start date

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/tasks",
            page=SyncTasksPage[Task],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "cursor": cursor,
                        "end": end,
                        "include_chunks": include_chunks,
                        "limit": limit,
                        "sort": sort,
                        "start": start,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            model=Task,
        )

    def delete(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a task by its ID.

        Requirements:

        - Task must have status `Succeeded` or `Failed`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def cancel(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Cancel a task that hasn't started processing yet:

        - For new tasks: Status will be updated to `Cancelled`
        - For updating tasks: Task will revert to the previous state

        Requirements:

        - Task must have status `Starting`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/task/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        task_id: Optional[str],
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Retrieves detailed information about a task by its ID, including:

        - Processing status
        - Task configuration
        - Output data (if processing is complete)
        - File metadata (name, page count)
        - Timestamps (created, started, finished)
        - Presigned URLs for accessing files

        This endpoint can be used to:

        1. Poll the task status during processing
        2. Retrieve the final output once processing is complete
        3. Access task metadata and configuration

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          include_chunks: Whether to include chunks in the output response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "include_chunks": include_chunks,
                    },
                    task_get_params.TaskGetParams,
                ),
            ),
            cast_to=Task,
        )


class AsyncTaskResource(AsyncAPIResource):
    @cached_property
    def parse(self) -> AsyncParseResource:
        return AsyncParseResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return AsyncTaskResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        cursor: Union[str, datetime] | NotGiven = NOT_GIVEN,
        end: Union[str, datetime] | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        start: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Task, AsyncTasksPage[Task]]:
        """Retrieves a list of tasks with cursor-based pagination.

        By default, tasks are
        returned in descending order (newest first).

        ## Default Behaviors:

        - **limit**: Returns all tasks if not specified
        - **start**: No start date filter (returns from beginning of time)
        - **end**: No end date filter (returns up to current time)
        - **cursor**: Starts from most recent tasks (no pagination offset)
        - **sort**: 'desc' (descending order, newest first)
        - **include_chunks**: false (excludes chunks for better performance)
        - **base64_urls**: false (returns presigned URLs instead of base64)

        ## Common Usage Patterns:

        **Basic usage (get all tasks):** `GET /api/v1/tasks`

        **Get first 10 tasks:** `GET /api/v1/tasks?limit=10`

        **Paginate through results:**

        1. First request: `GET /api/v1/tasks?limit=10`
        2. Use next_cursor from response for subsequent pages:
           `GET /api/v1/tasks?limit=10&cursor=<timestamp>`

        **Filter by date range:**
        `GET /api/v1/tasks?start=2025-01-01T00:00:00Z&end=2025-12-31T23:59:59Z`

        **Get detailed results with chunks:** `GET /api/v1/tasks?include_chunks=true`

        **Get base64 encoded content:** `GET /api/v1/tasks?base64_urls=true`

        **Get tasks in ascending order (oldest first):** `GET /api/v1/tasks?sort=asc`

        **Get tasks in descending order (newest first, default):**
        `GET /api/v1/tasks?sort=desc`

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          cursor: Cursor for pagination (timestamp)

          end: End date

          include_chunks: Whether to include chunks in the output response

          limit: Number of tasks per page

          sort: Sort order: 'asc' for ascending, 'desc' for descending (default)

          start: Start date

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/tasks",
            page=AsyncTasksPage[Task],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "cursor": cursor,
                        "end": end,
                        "include_chunks": include_chunks,
                        "limit": limit,
                        "sort": sort,
                        "start": start,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            model=Task,
        )

    async def delete(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a task by its ID.

        Requirements:

        - Task must have status `Succeeded` or `Failed`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def cancel(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Cancel a task that hasn't started processing yet:

        - For new tasks: Status will be updated to `Cancelled`
        - For updating tasks: Task will revert to the previous state

        Requirements:

        - Task must have status `Starting`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/task/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        task_id: Optional[str],
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Retrieves detailed information about a task by its ID, including:

        - Processing status
        - Task configuration
        - Output data (if processing is complete)
        - File metadata (name, page count)
        - Timestamps (created, started, finished)
        - Presigned URLs for accessing files

        This endpoint can be used to:

        1. Poll the task status during processing
        2. Retrieve the final output once processing is complete
        3. Access task metadata and configuration

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          include_chunks: Whether to include chunks in the output response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "include_chunks": include_chunks,
                    },
                    task_get_params.TaskGetParams,
                ),
            ),
            cast_to=Task,
        )


class TaskResourceWithRawResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.list = to_raw_response_wrapper(
            task.list,
        )
        self.delete = to_raw_response_wrapper(
            task.delete,
        )
        self.cancel = to_raw_response_wrapper(
            task.cancel,
        )
        self.get = to_raw_response_wrapper(
            task.get,
        )

    @cached_property
    def parse(self) -> ParseResourceWithRawResponse:
        return ParseResourceWithRawResponse(self._task.parse)


class AsyncTaskResourceWithRawResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.list = async_to_raw_response_wrapper(
            task.list,
        )
        self.delete = async_to_raw_response_wrapper(
            task.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            task.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            task.get,
        )

    @cached_property
    def parse(self) -> AsyncParseResourceWithRawResponse:
        return AsyncParseResourceWithRawResponse(self._task.parse)


class TaskResourceWithStreamingResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.list = to_streamed_response_wrapper(
            task.list,
        )
        self.delete = to_streamed_response_wrapper(
            task.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            task.cancel,
        )
        self.get = to_streamed_response_wrapper(
            task.get,
        )

    @cached_property
    def parse(self) -> ParseResourceWithStreamingResponse:
        return ParseResourceWithStreamingResponse(self._task.parse)


class AsyncTaskResourceWithStreamingResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.list = async_to_streamed_response_wrapper(
            task.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            task.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            task.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            task.get,
        )

    @cached_property
    def parse(self) -> AsyncParseResourceWithStreamingResponse:
        return AsyncParseResourceWithStreamingResponse(self._task.parse)
